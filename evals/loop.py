#!/usr/bin/env python3
"""Maintainer-only output feedback evaluation loop."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALS = ROOT / "evals"
AUDIT_PATH = ROOT / "skills/humanizer-kr/scripts/audit_korean_text.py"
SKILL_PATH = ROOT / "skills/humanizer-kr/SKILL.md"
SOURCE_RULES_PATH = ROOT / "skills/humanizer-kr/references/korean-source-rules.md"
spec = importlib.util.spec_from_file_location("audit_korean_text", AUDIT_PATH)
assert spec and spec.loader
audit_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit_module
spec.loader.exec_module(audit_module)


def parse_input(path: Path) -> tuple[dict[str, Any], str]:
    """Read the supported small YAML-like frontmatter without PyYAML."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.S)
    if not match:
        raise ValueError(f"{path}: invalid frontmatter")
    metadata: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            continue
        key, value = key.strip(), value.strip()
        if key == "must_keep":
            metadata[key] = json.loads(value)
        elif value in ("true", "false"):
            metadata[key] = value == "true"
        else:
            metadata[key] = value
    return metadata, match.group(2).strip()


def facts(source: str, output: str, must_keep: list[str]) -> dict[str, list[str]]:
    """Find required strings and source digit runs lost in the output."""
    normalized_output = output.replace(",", "")
    return {
        "missing_must_keep": [fact for fact in must_keep if fact.replace(",", "") not in normalized_output],
        "missing_numbers": [number for number in re.findall(r"\d+", source.replace(",", ""))
                            if number not in normalized_output],
    }


def input_files(evals_dir: Path) -> list[Path]:
    return sorted((evals_dir / "inputs").glob("*.ko.md"))


def make_prompt(body: str, condition: str) -> str:
    """Build the isolated generator prompt for one condition."""
    if condition == "plain":
        return "한국어 문장을 자연스럽게 다듬어 주세요.\n\n" + body
    skill_dir = SKILL_PATH.parent
    references = sorted((skill_dir / "references").glob("*.md"))
    return "\n\n".join(
        [SKILL_PATH.read_text(encoding="utf-8"), *(path.read_text(encoding="utf-8") for path in references), body,
         "return only the final rewrite"]
    )


def invoke(engine: str, model: str, text: str, temp_cwd: Path, codex_home: Path | None = None,
           judge: bool = False) -> str:
    """Call an isolated CLI engine, or echo for deterministic smoke tests."""
    if engine == "fake":
        return text
    if engine == "claude":
        system_prompt = "You are a strict Korean writing evaluator. Output only JSON." if judge else \
            "You are a careful Korean writing editor. Output only what the user asks for."
        result = subprocess.run(
            ["claude", "-p", "--setting-sources", "project", "--system-prompt", system_prompt,
             "--model", model, "--tools", ""], input=text, text=True, capture_output=True, cwd=temp_cwd,
        )
    else:
        assert codex_home is not None
        output_path = temp_cwd / "last-message.txt"
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(codex_home)
        result = subprocess.run(
            ["codex", "exec", "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check",
             "-C", str(temp_cwd), "--model", model, "-o", str(output_path), "-"],
            input=text, text=True, capture_output=True, cwd=temp_cwd, env=environment,
        )
        if result.returncode == 0:
            return output_path.read_text(encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"{engine} exited {result.returncode}")
    return result.stdout


def make_codex_home() -> tempfile.TemporaryDirectory[str]:
    """Create a temporary Codex home containing only the auth symlink."""
    temporary = tempfile.TemporaryDirectory(prefix="humanizer-codex-")
    source_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    auth_file = source_home / "auth.json"
    if auth_file.exists():
        (Path(temporary.name) / "auth.json").symlink_to(auth_file)
    return temporary


def run(args: argparse.Namespace) -> int:
    """Generate resumable output files for all selected input combinations."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    round_dir.mkdir(parents=True, exist_ok=True)
    if getattr(args, "engine_check", False):
        # A leaked global Korean-language instruction makes this English answer contain Hangul.
        probe = "What is the capital of France? Answer in one short English sentence."
        with tempfile.TemporaryDirectory(prefix="humanizer-probe-") as cwd:
            homes = make_codex_home() if "codex" in args.engines.split(",") else None
            try:
                for engine in args.engines.split(","):
                    model = args.codex_model if engine == "codex" else args.claude_model
                    answer = invoke(engine, model, probe, Path(cwd), Path(homes.name) if homes else None)
                    if re.search(r"[가-힣]", answer):
                        print(f"engine check failed ({engine}): {answer}", file=sys.stderr)
                        return 2
            finally:
                if homes:
                    homes.cleanup()
    if not (round_dir / "meta.json").exists():
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True)
        sha = result.stdout.strip() if result.returncode == 0 else "unknown"
        metadata = {"skill_sha": sha or "unknown", "models": {"codex": args.codex_model,
                    "claude": args.claude_model}, "date": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        (round_dir / "meta.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    tasks = []
    for path in input_files(evals_dir):
        meta, body = parse_input(path)
        for engine in args.engines.split(","):
            for condition in args.conditions.split(","):
                if args.round > 1 and condition == "plain":
                    continue
                destination = round_dir / "outputs" / engine / condition / f"{path.stem}.md"
                if not (destination.exists() and destination.stat().st_size):
                    tasks.append((path, body, engine, condition, destination))
    failures = False
    homes = make_codex_home() if "codex" in args.engines.split(",") else None
    def generate(task: tuple[Path, str, str, str, Path]) -> None:
        _, body, engine, condition, destination = task
        model = {"codex": args.codex_model, "claude": args.claude_model, "fake": "fake"}[engine]
        with tempfile.TemporaryDirectory(prefix="humanizer-run-") as cwd:
            output = invoke(engine, model, make_prompt(body, condition), Path(cwd), Path(homes.name) if homes else None)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [executor.submit(generate, task) for task in tasks]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as error:
                    failures = True
                    print(f"run failed: {error}", file=sys.stderr)
    finally:
        if homes:
            homes.cleanup()
    return 1 if failures else 0


def parse_verdict(raw: str, output: str | None = None) -> dict[str, Any]:
    """Parse fenced or embedded JSON and validate the judge schema."""
    candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    try:
        verdict = json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start < 0 or end < start:
            raise ValueError("judge response contains no JSON object") from None
        verdict = json.loads(candidate[start:end + 1])
    required = {"invented": list, "dropped_facts": list, "register_ok": bool, "reader_action_ok": bool,
                "genre_fit": int, "naturalness": int, "residual_tells": list, "note": str}
    if not isinstance(verdict, dict) or any(not isinstance(verdict.get(key), kind) for key, kind in required.items()):
        raise ValueError("judge JSON has missing fields or invalid field types")
    if any(not 1 <= verdict[key] <= 5 for key in ("genre_fit", "naturalness")):
        raise ValueError("judge scores must be integers from 1 to 5")
    violations = verdict.get("rule_violations", [])
    if not isinstance(violations, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("rule"), str)
        or not isinstance(item.get("quote"), str) for item in violations
    ):
        raise ValueError("judge rule_violations must be a list of rule/quote objects")
    if output is not None:
        violations = [item for item in violations if item["quote"] in output]
    verdict["rule_violations"] = violations
    return verdict


def judge_prompt(genre: str, must_keep: list[str], source: str, output: str) -> str:
    """Build an anonymized judge prompt with the skill's evaluation policy."""
    skill = SKILL_PATH.read_text(encoding="utf-8")
    rubric = skill[skill.index("## Naturalness Rubric"):skill.index("## Voice Calibration")]
    source_rules = SOURCE_RULES_PATH.read_text(encoding="utf-8")
    sourced_rules = source_rules[source_rules.index("## Sourced Sentence Rules"):source_rules.index("## Genre Strength Matrix")]
    genre_matrix = source_rules[source_rules.index("## Genre Strength Matrix"):]
    return (f"Evaluate this Korean rewrite. Genre: {genre}. must_keep: {json.dumps(must_keep, ensure_ascii=False)}\n\n"
            f"{rubric}\n{sourced_rules}\n{genre_matrix}\n"
            "For this genre, list each violation of a required or recommended sourced rule (S or N) in rule_violations "
            "as {\"rule\": \"S7 or N8\", \"quote\": \"<exact text from OUTPUT>\"}. "
            "Use an empty list when there are none.\n"
            "Field definitions: genre_fit and naturalness are integers 1-5; "
            "1 = clearly machine-like or wrong genre, 3 = acceptable but bland, "
            "5 = reads like a skilled native writer for this genre. dropped_facts means verifiable content only: "
            "names, numbers, dates, times, paths, conditions, required actions, and distinct events. "
            "Removed praise, filler, greetings, closing courtesies, and vague expectations are NOT dropped facts. "
            "List invented content (facts/benefits/numbers not in source, including a claim made stronger "
            "than the source such as an estimate turned into a promise) in invented. Return strict JSON with fields "
            "invented, dropped_facts, register_ok, reader_action_ok, genre_fit, naturalness, "
            "residual_tells, note, rule_violations. Do not identify the generator or condition.\nSOURCE:\n"
            f"{source}\nOUTPUT:\n{output}")


def judge(args: argparse.Namespace) -> int:
    """Judge all unjudged outputs concurrently and append resumable records."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    judge_file = round_dir / "judge.jsonl"
    existing = set()
    if judge_file.exists():
        for line in judge_file.read_text(encoding="utf-8").splitlines():
            try:
                existing.add(json.loads(line)["output"])
            except (ValueError, KeyError):
                continue
    tasks = []
    for output_path in sorted((round_dir / "outputs").glob("*/*/*.md")):
        key = str(output_path.relative_to(round_dir))
        if key not in existing:
            input_path = evals_dir / "inputs" / f"{output_path.stem[:-3]}.ko.md"
            metadata, source = parse_input(input_path)
            tasks.append((output_path, key, metadata, source))
    lock = threading.Lock()
    failures = False
    homes = make_codex_home() if args.judge_engine == "codex" else None
    judge_file.parent.mkdir(parents=True, exist_ok=True)
    def evaluate(task: tuple[Path, str, dict[str, Any], str]) -> None:
        output_path, key, metadata, source = task
        output = output_path.read_text(encoding="utf-8")
        if args.judge_engine == "fake":
            verdict = {"invented": [], "dropped_facts": [], "register_ok": True, "reader_action_ok": True,
                       "genre_fit": 3, "naturalness": 3, "residual_tells": [], "note": "fake deterministic verdict",
                       "rule_violations": []}
        else:
            with tempfile.TemporaryDirectory(prefix="humanizer-judge-") as cwd:
                raw = invoke(args.judge_engine, args.judge_model,
                             judge_prompt(metadata.get("genre", ""), metadata.get("must_keep", []), source, output),
                             Path(cwd), Path(homes.name) if homes else None, judge=True)
            try:
                verdict = parse_verdict(raw, output)
            except (ValueError, json.JSONDecodeError) as error:
                verdict = {"error": str(error), "raw": raw}
        row = {"output": key, "engine": output_path.parts[-3], "condition": output_path.parts[-2],
               "genre": metadata.get("genre"), "thin": metadata.get("thin", False), "verdict": verdict,
               "checks": facts(source, output, metadata.get("must_keep", [])),
               "audit_before": len(audit_module.audit(source)), "audit_after": len(audit_module.audit(output))}
        with lock, judge_file.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [executor.submit(evaluate, task) for task in tasks]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as error:
                    failures = True
                    print(f"judge failed: {error}", file=sys.stderr)
    finally:
        if homes:
            homes.cleanup()
    return 1 if failures else 0


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load valid JSON objects from a JSONL file."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pick(args: argparse.Namespace) -> int:
    """Show blind pairs and save resumable human choices."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    pick_file = round_dir / "picks.jsonl"
    previous = load_jsonl(pick_file)
    seed = previous[0]["seed"] if previous else (args.seed if args.seed is not None else random.randrange(2**32))
    done = {(row["input"], row["engine"]) for row in previous}
    rng = random.Random(seed)
    candidates = []
    for path in input_files(evals_dir):
        metadata, _ = parse_input(path)
        name = f"{path.stem}.md"
        for engine in args.engines.split(","):
            key = (path.name, engine)
            if key in done:
                continue
            if args.round == 1:
                current = round_dir / "outputs" / engine / "skill" / name
                baseline = round_dir / "outputs" / engine / "plain" / name
            else:
                current = round_dir / "outputs" / engine / "skill" / name
                baseline = evals_dir / "rounds" / str(args.round - 1) / "outputs" / engine / "skill" / name
            if current.exists() and baseline.exists():
                candidates.append((path, metadata, engine, current, baseline))
    rng.shuffle(candidates)
    chosen = candidates[:args.n]
    round_dir.mkdir(parents=True, exist_ok=True)
    if not previous and not chosen:
        pick_file.write_text(json.dumps({"seed": seed}, ensure_ascii=False) + "\n", encoding="utf-8")
    with pick_file.open("a", encoding="utf-8") as stream:
        for index, (path, metadata, engine, current, baseline) in enumerate(chosen, 1):
            current_first = bool(rng.getrandbits(1))
            a_path, b_path = (current, baseline) if current_first else (baseline, current)
            print(f"[{index}/{len(chosen)}] {metadata.get('genre')}\nSOURCE:\n{parse_input(path)[1]}\n\nA — {('current' if current_first else 'baseline')}:\n{a_path.read_text()}\n\nB — {('baseline' if current_first else 'current')}:\n{b_path.read_text()}\n")
            answer = input("a/b/t/q: ").strip().lower()
            if answer == "q":
                break
            if answer not in ("a", "b", "t"):
                print("Please enter a, b, t, or q.", file=sys.stderr)
                continue
            stream.write(json.dumps({"input": path.name, "engine": engine, "seed": seed,
                                     "a_label": "current" if current_first else "baseline",
                                     "b_label": "baseline" if current_first else "current",
                                     "winner": answer, "genre": metadata.get("genre")}, ensure_ascii=False) + "\n")
    return 0


def report(args: argparse.Namespace) -> int:
    """Write aggregate quality, human-choice, and round-delta metrics."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    round_dir.mkdir(parents=True, exist_ok=True)
    rows = load_jsonl(round_dir / "judge.jsonl")
    valid_rows = [row for row in rows if "error" not in row["verdict"]]
    hard_causes = {"invented": 0, "dropped_facts": 0, "missing_must_keep": 0, "missing_numbers": 0}
    for row in rows:
        verdict, checks = row["verdict"], row["checks"]
        row["hard_fail"] = bool(verdict.get("invented") or verdict.get("dropped_facts") or
                                 checks["missing_must_keep"] or checks["missing_numbers"])
        for cause, present in (("invented", verdict.get("invented")), ("dropped_facts", verdict.get("dropped_facts")),
                               ("missing_must_keep", checks["missing_must_keep"]),
                               ("missing_numbers", checks["missing_numbers"])):
            hard_causes[cause] += bool(present)
    lines = [f"# Round {args.round} report", "", f"Outputs judged: {len(rows)}",
             f"Judge errors: {len(rows) - len(valid_rows)}"]
    lines.extend(["", f"Hard-fail rate: {sum(row['hard_fail'] for row in rows)}/{len(rows)}" if rows else "Hard-fail rate: n/a"])
    lines.extend([f"- {cause}: {count}" for cause, count in hard_causes.items()])
    groups = sorted({(row["engine"], row["condition"]) for row in rows})
    for engine, condition in groups:
        group_rows = [row for row in rows if row["engine"] == engine and row["condition"] == condition]
        lines.append(f"- {engine} / {condition}: {sum(row['hard_fail'] for row in group_rows)}/{len(group_rows)}")
        for cause in hard_causes:
            count = sum(bool(row["verdict"].get(cause)) if cause in ("invented", "dropped_facts") else bool(row["checks"].get(cause)) for row in group_rows)
            lines.append(f"  - {cause}: {count}")
    lines.extend(["", "## Sourced rule violations", ""])
    total_violating = sum(bool(row["verdict"].get("rule_violations", [])) for row in rows)
    overall_rate = total_violating / len(rows) if rows else None
    lines.append(
        f"Outputs with any sourced-rule violation: {total_violating}/{len(rows)} ({overall_rate:.1%})"
        if overall_rate is not None else "Outputs with any sourced-rule violation: n/a"
    )
    for engine, condition in groups:
        group_rows = [row for row in rows if row["engine"] == engine and row["condition"] == condition]
        affected = sum(bool(row["verdict"].get("rule_violations", [])) for row in group_rows)
        rate = affected / len(group_rows) if group_rows else None
        lines.append(
            f"- {engine} / {condition}: outputs with violations {affected}/{len(group_rows)} ({rate:.1%})"
            if rate is not None else f"- {engine} / {condition}: outputs with violations n/a"
        )
        counts: dict[str, int] = {}
        for row in group_rows:
            for violation in row["verdict"].get("rule_violations", []):
                rule_id = violation["rule"]
                counts[rule_id] = counts.get(rule_id, 0) + 1
        for rule_id, count in sorted(counts.items()):
            lines.append(f"  - {rule_id}: {count}")
    for field in ("naturalness", "genre_fit"):
        lines.extend(["", f"## Mean {field}", "", "| Genre | " + " | ".join(f"{e}/{c}" for e, c in groups) + " |", "|---|" + "---|" * len(groups)])
        for genre in sorted({row.get("genre", "") for row in valid_rows}):
            cells = []
            for engine, condition in groups:
                values = [row["verdict"][field] for row in valid_rows if row["genre"] == genre and row["engine"] == engine and row["condition"] == condition]
                cells.append(f"{sum(values)/len(values):.2f}" if values else "n/a")
            lines.append(f"| {genre} | " + " | ".join(cells) + " |")
        cells = []
        for engine, condition in groups:
            values = [row["verdict"][field] for row in valid_rows if row["engine"] == engine and row["condition"] == condition]
            cells.append(f"{sum(values)/len(values):.2f}" if values else "n/a")
        lines.append("| Overall | " + " | ".join(cells) + " |")
    audit_groups = []
    for engine, condition in groups:
        subset = [row for row in rows if row["engine"] == engine and row["condition"] == condition]
        before = sum(row["audit_before"] for row in subset) / len(subset) if subset else 0
        after = sum(row["audit_after"] for row in subset) / len(subset) if subset else 0
        audit_groups.append(f"{engine}/{condition}: {before:.2f} -> {after:.2f}")
    lines.extend(["", "Audit findings mean before -> after: " + ("; ".join(audit_groups) if audit_groups else "n/a")])
    picks = [pick for pick in load_jsonl(round_dir / "picks.jsonl") if "winner" in pick]
    decisive = [pick for pick in picks if pick["winner"] in ("a", "b")]
    current_wins = sum(pick[f"{pick['winner']}_label"] == "current" for pick in decisive)
    ties = sum(pick["winner"] == "t" for pick in picks)
    if picks:
        lines.append(f"Human win rate (current): {current_wins}/{len(decisive)}" if decisive else "Human win rate: n/a (no decisive picks)")
        lines.append(f"Human ties: {ties}")
    else:
        lines.append("Human win rate: n/a (no picks)")
        lines.append("Human ties: 0")
    disagreements = []
    by_output = {row["output"]: row for row in rows}
    for pick in picks:
        if pick["winner"] not in ("a", "b"):
            continue
        current_path = f"outputs/{pick['engine']}/skill/{Path(pick['input']).stem}.md"
        baseline_condition = "plain" if args.round == 1 else "skill"
        baseline_round = round_dir if args.round == 1 else evals_dir / "rounds" / str(args.round - 1)
        baseline_path = f"outputs/{pick['engine']}/{baseline_condition}/{Path(pick['input']).stem}.md"
        if baseline_round != round_dir:
            continue
        current_row, baseline_row = by_output.get(current_path), by_output.get(baseline_path)
        if not current_row or not baseline_row or "error" in current_row["verdict"] or "error" in baseline_row["verdict"]:
            continue
        human_label = pick[f"{pick['winner']}_label"]
        judge_label = "current" if current_row["verdict"]["naturalness"] > baseline_row["verdict"]["naturalness"] else "baseline"
        if current_row["verdict"]["naturalness"] != baseline_row["verdict"]["naturalness"] and human_label != judge_label:
            disagreements.append(pick["input"])
    lines.extend([f"Judge-human disagreements: {len(disagreements)}", *(f"- {item}" for item in disagreements)])
    humans = list((evals_dir / "human").glob("*.ko.md")) if (evals_dir / "human").exists() else []
    flagged = sum(bool(audit_module.audit(path.read_text(encoding="utf-8"))) for path in humans)
    lines.append(f"Audit false-positive rate: {flagged}/{len(humans)}" if humans else "Audit false-positive rate: n/a")
    if args.round > 1:
        previous = load_jsonl(evals_dir / "rounds" / str(args.round - 1) / "judge.jsonl")
        if previous:
            lines.extend(["", f"## Delta vs round {args.round - 1}"])
            for metric in ("hard_fail", "naturalness", "genre_fit"):
                for engine in sorted({row["engine"] for row in rows + previous}):
                    old = [row for row in previous if row["engine"] == engine and row["condition"] == "skill" and "error" not in row["verdict"]]
                    new = [row for row in rows if row["engine"] == engine and row["condition"] == "skill" and "error" not in row["verdict"]]
                    if metric == "hard_fail":
                        old_values = [bool(row["verdict"].get("invented") or row["verdict"].get("dropped_facts") or row["checks"]["missing_must_keep"] or row["checks"]["missing_numbers"]) for row in old]
                        new_values = [bool(row["verdict"].get("invented") or row["verdict"].get("dropped_facts") or row["checks"]["missing_must_keep"] or row["checks"]["missing_numbers"]) for row in new]
                        old_mean, new_mean = (sum(old_values) / len(old_values) if old_values else None), (sum(new_values) / len(new_values) if new_values else None)
                    else:
                        old_mean = sum(row["verdict"][metric] for row in old) / len(old) if old else None
                        new_mean = sum(row["verdict"][metric] for row in new) / len(new) if new else None
                    lines.append(f"- {engine} {metric}: {old_mean if old_mean is not None else 'n/a'} -> {new_mean if new_mean is not None else 'n/a'}")
    report_text = "\n".join(lines) + "\n"
    (round_dir / "report.md").write_text(report_text, encoding="utf-8")
    print(report_text, end="")
    return 0


def main() -> None:
    """Parse the four public subcommands."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--round", type=int, required=True)
        command.add_argument("--evals-dir", default=str(DEFAULT_EVALS))
    run_parser = commands.add_parser("run")
    common(run_parser)
    run_parser.add_argument("--engines", default="codex")
    run_parser.add_argument("--conditions", default="skill,plain")
    run_parser.add_argument("--jobs", type=int, default=4)
    run_parser.add_argument("--codex-model", default="gpt-6-luna")
    run_parser.add_argument("--claude-model", default="claude-sonnet-5-5")
    run_parser.add_argument("--engine-check", action="store_true")
    run_parser.set_defaults(handler=run)
    judge_parser = commands.add_parser("judge")
    common(judge_parser)
    judge_parser.add_argument("--judge-engine", default="claude")
    judge_parser.add_argument("--judge-model", default="claude-opus-5-5")
    judge_parser.add_argument("--jobs", type=int, default=4)
    judge_parser.set_defaults(handler=judge)
    pick_parser = commands.add_parser("pick")
    common(pick_parser)
    pick_parser.add_argument("--n", type=int, default=10)
    pick_parser.add_argument("--seed", type=int)
    pick_parser.add_argument("--engines", default="codex,claude")
    pick_parser.set_defaults(handler=pick)
    report_parser = commands.add_parser("report")
    common(report_parser)
    report_parser.set_defaults(handler=report)
    args = parser.parse_args()
    raise SystemExit(args.handler(args))


if __name__ == "__main__":
    main()

