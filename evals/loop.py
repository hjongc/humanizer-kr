#!/usr/bin/env python3
"""Maintainer-only output feedback evaluation loop."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import os
import random
import re
import statistics
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


def output_identity(output_path: Path) -> tuple[str, int]:
    """Return the source input stem and sample number for an output file."""
    match = re.fullmatch(r"(.+)~([1-9]\d*)", output_path.stem)
    sample = int(match.group(2)) if match else 1
    return (match.group(1), sample) if match and sample > 1 else (output_path.stem, 1)


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    """Return the two-sided 95% Wilson score interval for a rate."""
    if not total:
        return (0.0, 0.0)
    rate = successes / total
    z = 1.959963984540054
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    margin = z * ((rate * (1 - rate) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return (max(0.0, center - margin), min(1.0, center + margin))


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
    if getattr(args, "samples", 1) < 1:
        raise ValueError("--samples must be at least 1")
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
    meta_path = round_dir / "meta.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    if not metadata:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True)
        sha = result.stdout.strip() if result.returncode == 0 else "unknown"
        metadata = {"skill_sha": sha or "unknown", "models": {"codex": args.codex_model,
                    "claude": args.claude_model}, "date": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    skill_files = [SKILL_PATH, *sorted(SKILL_PATH.parent.joinpath("references").glob("*.md"))]
    digest = hashlib.sha256()
    for path in skill_files:
        digest.update(path.read_bytes())
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "skills"], cwd=ROOT,
                           text=True, capture_output=True)
    metadata.update({"skill_digest": digest.hexdigest(), "skill_dirty": bool(dirty.stdout.strip())})
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    tasks = []
    conditions = args.conditions.split(",")
    if getattr(args, "with_plain", False) and "plain" not in conditions:
        conditions.append("plain")
    for path in input_files(evals_dir):
        meta, body = parse_input(path)
        for engine in args.engines.split(","):
            for condition in conditions:
                if args.round > 1 and condition == "plain" and not getattr(args, "with_plain", False):
                    continue
                for sample in range(1, getattr(args, "samples", 1) + 1):
                    suffix = f"~{sample}" if sample > 1 else ""
                    destination = round_dir / "outputs" / engine / condition / f"{path.stem}{suffix}.md"
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
    required = {"invented": list, "dropped_facts": list, "register_ok": bool,
                "ai_tells": list, "human_likeness": int, "note": str, "rule_violations": list}
    if not isinstance(verdict, dict) or any(not isinstance(verdict.get(key), kind) for key, kind in required.items()):
        raise ValueError("judge JSON has missing fields or invalid field types")
    if not 1 <= verdict["human_likeness"] <= 5:
        raise ValueError("human_likeness must be an integer from 1 to 5")
    if any(not isinstance(item, dict) or not isinstance(item.get("tell"), str)
           or not isinstance(item.get("quote"), str) for item in verdict["ai_tells"]):
        raise ValueError("judge ai_tells must be a list of tell/quote objects")
    violations = verdict.get("rule_violations", [])
    if not isinstance(violations, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("rule"), str)
        or not isinstance(item.get("quote"), str)
        or ("introduced" in item and not isinstance(item["introduced"], bool)) for item in violations
    ):
        raise ValueError("judge rule_violations must be a list of rule/quote objects")
    for violation in violations:
        violation.setdefault("introduced", True)
    if output is not None:
        violations = [item for item in violations if item["quote"] in output]
        verdict["ai_tells"] = [item for item in verdict["ai_tells"] if item["quote"] in output]
    verdict["rule_violations"] = violations
    return verdict


def judge_prompt(genre: str, must_keep: list[str], source: str, output: str) -> str:
    """Build an anonymized judge prompt with the skill's evaluation policy."""
    skill = SKILL_PATH.read_text(encoding="utf-8")
    heading = "## Korean AI-Writing Tells"
    start = skill.find(heading)
    if start < 0:
        raise ValueError(f"{SKILL_PATH}: missing {heading} heading")
    next_heading = re.search(r"^## .+", skill[start + len(heading):], re.M)
    end = start + len(heading) + next_heading.start() if next_heading else len(skill)
    tells = skill[start:end].rstrip()
    source_rules = SOURCE_RULES_PATH.read_text(encoding="utf-8")
    sourced_rules = source_rules[source_rules.index("## Sourced Sentence Rules"):source_rules.index("## Genre Strength Matrix")]
    genre_matrix = source_rules[source_rules.index("## Genre Strength Matrix"):]
    return (f"Evaluate this Korean rewrite. Genre: {genre}. must_keep: {json.dumps(must_keep, ensure_ascii=False)}\n\n"
            f"{tells}\n{sourced_rules}\n{genre_matrix}\n"
            "Sourced rule violations are secondary to human-likeness and factual preservation. For this genre, list each violation of a required or recommended sourced rule (S or N) in rule_violations "
            "as {\"rule\": \"S7 or N8\", \"quote\": \"<exact text from OUTPUT>\", \"introduced\": true|false}. "
            "Set introduced=true when OUTPUT created the problem or could have fixed it using only content in SOURCE; "
            "set false when it inherited a problem from SOURCE and fixing it would require facts SOURCE does not give. "
            "Use an empty list when there are none.\n"
            "Field definitions: human_likeness is how likely a Korean reader would believe a person wrote OUTPUT, "
            "judged by the absence of AI-writing tells and translationese. 1 = obviously machine-written, "
            "3 = some tells remain, 5 = no tells; reads as an ordinary person's writing. It is NOT a quality score: "
            "do not reward OUTPUT for being more structured, complete, persuasive, or useful than SOURCE; "
            "a plain, slightly rough human sentence beats a polished, generic one. ai_tells lists every remaining "
            "tell in OUTPUT with its exact quote. dropped_facts means verifiable content only: "
            "names, numbers, dates, times, paths, conditions, required actions, and distinct events. "
            "Removed praise, filler, greetings, closing courtesies, and vague expectations are NOT dropped facts. "
            "List invented content (facts/benefits/numbers not in source, including a claim made stronger "
            "than the source such as an estimate turned into a promise) in invented. Invented also includes changes "
            "of modality or tense: requirement -> permission (\"입력하고\" -> \"입력할 수 있고\"), possibility -> "
            "assertion (\"제공이 가능합니다\" -> \"제공합니다\"), estimate -> confirmed fact, restriction -> "
            "full block, and completed -> upcoming. Content OUTPUT adds that SOURCE lacks (new reader actions, "
            "headings, lists, examples, emphasis) counts as invented only when it asserts something; otherwise "
            "mention it in note. Return strict JSON with fields invented, dropped_facts, register_ok, ai_tells "
            "([{\"tell\": \"short label\", \"quote\": \"exact text from OUTPUT\"}]), "
            "human_likeness (integer 1-5), note, rule_violations. Do not identify the generator or condition.\nSOURCE:\n"
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
            input_stem, sample = output_identity(output_path)
            input_path = evals_dir / "inputs" / f"{input_stem}.md"
            metadata, source = parse_input(input_path)
            tasks.append((output_path, key, metadata, source, sample))
    lock = threading.Lock()
    failures = False
    homes = make_codex_home() if args.judge_engine == "codex" else None
    judge_file.parent.mkdir(parents=True, exist_ok=True)
    def evaluate(task: tuple[Path, str, dict[str, Any], str, int]) -> None:
        output_path, key, metadata, source, sample = task
        output = output_path.read_text(encoding="utf-8")
        if args.judge_engine == "fake":
            verdict = {"invented": [], "dropped_facts": [], "register_ok": True,
                       "ai_tells": [], "human_likeness": 3, "note": "fake deterministic verdict",
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
        row = {"output": key, "sample": sample, "engine": output_path.parts[-3], "condition": output_path.parts[-2],
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


def _hard_fail(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    verdict, checks = row.get("verdict", {}), row.get("checks", {})
    return bool(verdict.get("invented") or verdict.get("dropped_facts") or
                checks.get("missing_must_keep") or checks.get("missing_numbers"))


def _pair_winner(raw: str) -> str:
    candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    try:
        result = json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start < 0 or end < start:
            raise ValueError("pair judge response contains no JSON object") from None
        result = json.loads(candidate[start:end + 1])
    if not isinstance(result, dict) or result.get("winner") not in ("A", "B", "tie") or not isinstance(result.get("reason"), str):
        raise ValueError("pair judge JSON must contain winner A/B/tie and reason")
    return result["winner"]


def pair(args: argparse.Namespace) -> int:
    """Compare skill outputs with plain outputs and source, resuming pair records."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    pair_file = round_dir / "pair.jsonl"
    existing = {(row.get("input"), row.get("engine"), row.get("comparison"), row.get("sample", 1))
                for row in load_jsonl(pair_file)}
    judged = {row.get("output"): row for row in load_jsonl(round_dir / "judge.jsonl")}
    pending = []
    for skill_path in sorted((round_dir / "outputs").glob("*/skill/*.md")):
        input_stem, sample = output_identity(skill_path)
        input_path = evals_dir / "inputs" / f"{input_stem}.md"
        if not input_path.exists() or (sample > 1 and not getattr(args, "all_samples", False)):
            continue
        metadata, source = parse_input(input_path)
        filename = f"{input_stem}.md"
        engine = skill_path.parts[-3]
        plain_path = round_dir / "outputs" / engine / "plain" / filename
        comparisons = [("skill_vs_plain", plain_path, plain_path.read_text(encoding="utf-8") if plain_path.exists() else None),
                       ("skill_vs_source", None, source)]
        for comparison, other_path, other_text in comparisons:
            key = (input_path.name, engine, comparison, sample)
            if key in existing or other_text is None:
                continue
            skill_key = str(skill_path.relative_to(round_dir))
            other_key = str(other_path.relative_to(round_dir)) if other_path else None
            pending.append((input_path.name, engine, comparison, sample, skill_path.read_text(encoding="utf-8"),
                            other_text, judged.get(skill_key), judged.get(other_key)))
    round_dir.mkdir(parents=True, exist_ok=True)
    homes = make_codex_home() if args.judge_engine == "codex" else None
    try:
        with pair_file.open("a", encoding="utf-8") as stream:
            for input_name, engine, comparison, sample, skill_text, other_text, skill_judge, other_judge in pending:
                forfeit = _hard_fail(skill_judge) or _hard_fail(other_judge)
                if forfeit:
                    result, orders = ("loss" if _hard_fail(skill_judge) else "win"), []
                elif args.judge_engine == "fake":
                    result, orders = "tie", ["tie", "tie"]
                else:
                    winners = []
                    for a_text, b_text in ((skill_text, other_text), (other_text, skill_text)):
                        prompt = ("Which text reads more like a person wrote it? Ignore which is more polished, "
                                  "complete, or useful. Return strict JSON {\"winner\": \"A\"|\"B\"|\"tie\", "
                                  "\"reason\": \"...\"}.\nA:\n" + a_text + "\nB:\n" + b_text)
                        with tempfile.TemporaryDirectory(prefix="humanizer-pair-") as cwd:
                            raw = invoke(args.judge_engine, args.judge_model, prompt, Path(cwd),
                                         Path(homes.name) if homes else None, judge=True)
                        winners.append(_pair_winner(raw))
                    orders = winners
                    result = "win" if winners == ["A", "B"] else "loss" if winners == ["B", "A"] else "tie"
                row = {"input": input_name, "sample": sample, "engine": engine, "comparison": comparison,
                       "result": result, "orders": orders, "forfeit": forfeit}
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    finally:
        if homes:
            homes.cleanup()
    return 0


def text_stats(text: str) -> dict[str, float]:
    """Compute simple sentence rhythm and nominalization proxies."""
    lines = text.splitlines()
    filtered = []
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or re.match(r"^\s*#{1,6}(?:\s|$)", line):
            continue
        filtered.append(line)
    body = "\n".join(filtered)
    sentences = [part.strip() for part in re.split(r"(?<=[.?!…])(?=\s|$)|[\r\n]+", body) if part.strip()]
    lengths = [len(re.sub(r"\s", "", sentence)) for sentence in sentences]
    mean_length = statistics.mean(lengths) if lengths else 0.0
    cv = statistics.pstdev(lengths) / mean_length if len(lengths) > 1 and mean_length else 0.0
    endings = set()
    for sentence in sentences:
        hangul = re.findall(r"[가-힣]", sentence)
        if len(hangul) >= 2:
            endings.add("".join(hangul[-2:]))
    connectors = ("또한", "이를 통해", "아울러", "더불어", "나아가", "따라서", "특히", "이에", "결론적으로", "무엇보다")
    connector_count = sum(sentence.startswith(connectors) for sentence in sentences)
    tokens = body.split()
    # shortcut: regex proxy for nominalization, replace with a morphological analyzer if the metric drives decisions
    nominal_pattern = re.compile(r"^(?:[가-힣]{2,}(?:화|성)(?:을|를|이|가|은|는|의|에|과|와|도|으로|로)?[.,]?|[가-힣]+적(?:인|으로)[.,]?)$")
    nominal_count = sum(bool(nominal_pattern.match(token)) for token in tokens)
    return {"sent_len_mean": mean_length, "sent_len_cv": cv,
            "ending_diversity": len(endings) / len(sentences) if sentences else 0.0,
            "connector_rate": connector_count / len(sentences) if sentences else 0.0,
            "nominal_rate": nominal_count * 100 / len(tokens) if tokens else 0.0}


STAT_METRICS = ("sent_len_mean", "sent_len_cv", "ending_diversity", "connector_rate", "nominal_rate")


def compute_stats(evals_dir: Path, round_dir: Path, human_dir: Path | None) -> dict[str, Any]:
    groups: dict[str, list[dict[str, float]]] = {"source": []}
    for path in input_files(evals_dir):
        groups["source"].append(text_stats(parse_input(path)[1]))
    for output in sorted((round_dir / "outputs").glob("*/*/*.md")):
        group = f"{output.parts[-3]}/{output.parts[-2]}"
        groups.setdefault(group, []).append(text_stats(output.read_text(encoding="utf-8")))
    result = {name: {"count": len(values), "mean": {
        metric: sum(item[metric] for item in values) / len(values) for metric in STAT_METRICS
    } if values else {metric: None for metric in STAT_METRICS}} for name, values in groups.items()}
    if human_dir and human_dir.is_dir():
        human_values = [text_stats(path.read_text(encoding="utf-8")) for path in sorted(human_dir.glob("*.md"))]
        result["human"] = {"count": len(human_values), "mean": {
            metric: sum(item[metric] for item in human_values) / len(human_values) for metric in STAT_METRICS
        } if human_values else {metric: None for metric in STAT_METRICS}}
    else:
        result["human"] = None
    return result


def stats(args: argparse.Namespace) -> int:
    """Write aggregate objective statistics without retaining human reference text."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    human_arg = getattr(args, "human", None)
    human_dir = Path(human_arg).expanduser() if human_arg else Path.home() / ".humanizer-kr/samples"
    values = compute_stats(evals_dir, round_dir, human_dir if human_dir.is_dir() else None)
    round_dir.mkdir(parents=True, exist_ok=True)
    path = round_dir / "stats.json"
    path.write_text(json.dumps(values, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Objective statistics written: {path}")
    print(f"human reference: {values['human']['count']} files" if values["human"] else "human reference: none")
    return 0


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
    for current in sorted((round_dir / "outputs").glob("*/skill/*.md")):
        input_stem, sample = output_identity(current)
        engine = current.parts[-3]
        path = evals_dir / "inputs" / f"{input_stem}.md"
        key = (path.name, engine)
        if sample != 1 or engine not in args.engines.split(",") or not path.exists() or key in done:
            continue
        metadata, _ = parse_input(path)
        name = f"{input_stem}.md"
        if args.round == 1:
            baseline = round_dir / "outputs" / engine / "plain" / name
        else:
            plain = round_dir / "outputs" / engine / "plain" / name
            baseline = plain if plain.exists() else \
                evals_dir / "rounds" / str(args.round - 1) / "outputs" / engine / "skill" / name
        if baseline.exists():
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
    """Write factual, human-likeness, pairwise, objective and secondary metrics."""
    evals_dir = Path(args.evals_dir)
    round_dir = evals_dir / "rounds" / str(args.round)
    round_dir.mkdir(parents=True, exist_ok=True)
    rows = load_jsonl(round_dir / "judge.jsonl")
    valid_rows = [row for row in rows if "error" not in row.get("verdict", {})]
    groups = sorted({(row["engine"], row["condition"]) for row in rows})
    for row in rows:
        row["hard_fail"] = _hard_fail(row)
        row["sample"] = row.get("sample", output_identity(Path(row["output"]))[1])
    lines = [f"# Round {args.round} report", "", f"Outputs judged: {len(rows)}",
             f"Judge errors: {len(rows) - len(valid_rows)}", "",
             f"Hard-fail rate (facts): {sum(row['hard_fail'] for row in rows)}/{len(rows)}" if rows else "Hard-fail rate (facts): n/a"]
    for engine, condition in groups:
        subset = [row for row in rows if (row["engine"], row["condition"]) == (engine, condition)]
        failures = sum(row["hard_fail"] for row in subset)
        lower, upper = wilson_interval(failures, len(subset))
        lines.append(f"- {engine} / {condition}: hard-fail outputs {failures}/{len(subset)}; "
                     f"Wilson 95% interval {lower:.1%}–{upper:.1%}")
        input_samples: dict[str, list[bool]] = {}
        for row in subset:
            input_stem, _ = output_identity(Path(row["output"]))
            input_samples.setdefault(input_stem, []).append(row["hard_fail"])
        if any(len(samples) > 1 for samples in input_samples.values()):
            failing_some = sum(any(samples) for samples in input_samples.values())
            failing_all = sum(all(samples) for samples in input_samples.values())
            lines.append(f"  - inputs failing in >= 1 sample: {failing_some}/{len(input_samples)}")
            lines.append(f"  - inputs failing in all samples: {failing_all}/{len(input_samples)}")

    fields = {field for row in valid_rows for field in row.get("verdict", {})}
    for field in ("human_likeness", "naturalness", "genre_fit"):
        if field not in fields:
            continue
        lines.extend(["", f"## Mean {field}", "", "| Genre | " + " | ".join(f"{e}/{c}" for e, c in groups) + " |",
                      "|---|" + "---|" * len(groups)])
        for genre in sorted({row.get("genre", "") for row in valid_rows if field in row.get("verdict", {})}):
            cells = []
            for engine, condition in groups:
                values = [row["verdict"][field] for row in valid_rows if row.get("genre") == genre and
                          row["engine"] == engine and row["condition"] == condition and field in row.get("verdict", {})]
                cells.append(f"{sum(values) / len(values):.2f}" if values else "n/a")
            lines.append(f"| {genre} | " + " | ".join(cells) + " |")
        values = []
        for engine, condition in groups:
            group_values = [row["verdict"][field] for row in valid_rows if row["engine"] == engine and
                            row["condition"] == condition and field in row.get("verdict", {})]
            values.append(f"{sum(group_values) / len(group_values):.2f}" if group_values else "n/a")
        lines.append("| Overall | " + " | ".join(values) + " |")

    lines.extend(["", "## AI tells", ""])
    for engine, condition in groups:
        subset = [row for row in valid_rows if (row["engine"], row["condition"]) == (engine, condition)
                  and "ai_tells" in row.get("verdict", {})]
        tells = [tell for row in subset for tell in row.get("verdict", {}).get("ai_tells", [])]
        counts: dict[str, int] = {}
        for tell in tells:
            label = tell.get("tell", "")
            counts[label] = counts.get(label, 0) + 1
        mean = len(tells) / len(subset) if subset else None
        lines.append(f"- {engine} / {condition}: mean {mean:.2f}" if mean is not None else f"- {engine} / {condition}: n/a")
        lines.append("  - top tells: " + (", ".join(f"{name} ({count})" for name, count in
                     sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:10]) or "none"))

    lines.extend(["", "## Pairwise", ""])
    pair_rows = load_jsonl(round_dir / "pair.jsonl")
    if pair_rows:
        for engine, comparison in sorted({(row["engine"], row["comparison"]) for row in pair_rows}):
            subset = [row for row in pair_rows if row["engine"] == engine and row["comparison"] == comparison]
            counts = {result: sum(row["result"] == result for row in subset) for result in ("win", "tie", "loss")}
            lines.append(f"- {engine} / {comparison}: win {counts['win']}, tie {counts['tie']}, loss {counts['loss']}, "
                         f"forfeits {sum(bool(row.get('forfeit')) for row in subset)}")
    else:
        lines.append("n/a")

    human_arg = getattr(args, "human", None)
    human_dir = Path(human_arg).expanduser() if human_arg else Path.home() / ".humanizer-kr/samples"
    stats_path = round_dir / "stats.json"
    objective = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else \
        compute_stats(evals_dir, round_dir, human_dir if human_dir.is_dir() else None)
    lines.extend(["", "## Objective stats vs human", ""])
    human_stats = objective.get("human")
    lines.append(f"human reference: {human_stats['count']} files" if human_stats else "human reference: none")
    for group, values in objective.items():
        if group == "human":
            continue
        mean = values.get("mean", {})
        distances = [f"{metric} {mean[metric]:.3f} (distance {abs(mean[metric] - human_stats['mean'][metric]):.3f})"
                     if mean.get(metric) is not None and human_stats and human_stats.get("mean", {}).get(metric) is not None
                     else f"{metric} {mean.get(metric) if mean.get(metric) is not None else 'n/a'} (distance n/a)"
                     for metric in STAT_METRICS]
        lines.append(f"- {group} (n={values.get('count', 0)}): " + "; ".join(distances))

    lines.extend(["", "## Sourced rule violations", ""])
    introduced_violating = sum(any(item.get("introduced", True) for item in row.get("verdict", {}).get("rule_violations", [])) for row in rows)
    rate = introduced_violating / len(rows) if rows else None
    lines.append(f"Outputs with any introduced sourced-rule violation: {introduced_violating}/{len(rows)} ({rate:.1%})" if rate is not None else "Outputs with any introduced sourced-rule violation: n/a")
    total_violating = sum(bool(row.get("verdict", {}).get("rule_violations", [])) for row in rows)
    lines.append(f"Including inherited: {total_violating}/{len(rows)} outputs with violations")
    for engine, condition in groups:
        subset = [row for row in rows if (row["engine"], row["condition"]) == (engine, condition)]
        violations = [v for row in subset for v in row.get("verdict", {}).get("rule_violations", [])]
        introduced_counts: dict[str, int] = {}
        total_counts: dict[str, int] = {}
        for violation in violations:
            rule_id = violation.get("rule", "unknown")
            total_counts[rule_id] = total_counts.get(rule_id, 0) + 1
            if violation.get("introduced", True):
                introduced_counts[rule_id] = introduced_counts.get(rule_id, 0) + 1
        lines.append(f"- {engine} / {condition}: introduced {sum(introduced_counts.values())}; total {len(violations)}")
        lines.extend(f"  - {rule_id}: {count}" for rule_id, count in sorted(introduced_counts.items()))
        lines.append("  - including inherited: " + ", ".join(f"{rule_id} {count}" for rule_id, count in sorted(total_counts.items())))
    audit_groups = []
    for engine, condition in groups:
        subset = [row for row in rows if (row["engine"], row["condition"]) == (engine, condition)]
        before = sum(row.get("audit_before", 0) for row in subset) / len(subset) if subset else 0
        after = sum(row.get("audit_after", 0) for row in subset) / len(subset) if subset else 0
        audit_groups.append(f"{engine}/{condition}: {before:.2f} -> {after:.2f}")
    lines.extend(["", "## Audit findings", "", "Mean before -> after: " + ("; ".join(audit_groups) if audit_groups else "n/a")])
    picks = [pick for pick in load_jsonl(round_dir / "picks.jsonl") if "winner" in pick]
    decisive = [pick for pick in picks if pick["winner"] in ("a", "b")]
    current_wins = sum(pick.get(f"{pick['winner']}_label") == "current" for pick in decisive)
    ties = sum(pick["winner"] == "t" for pick in picks)
    lines.extend(["", "## Human picks", "", f"Human win rate (current): {current_wins}/{len(decisive)}" if decisive else
                  "Human win rate: n/a (no picks)" if not picks else "Human win rate: n/a (no decisive picks)",
                  f"Human ties: {ties}"])

    if args.round > 1:
        previous = load_jsonl(evals_dir / "rounds" / str(args.round - 1) / "judge.jsonl")
        if previous:
            lines.extend(["", f"## Delta vs round {args.round - 1}"])
            for engine in sorted({row["engine"] for row in rows + previous}):
                old_skill = [row for row in previous if row["engine"] == engine and row["condition"] == "skill"]
                new_skill = [row for row in rows if row["engine"] == engine and row["condition"] == "skill"]
                old_inputs = {output_identity(Path(row["output"]))[0] for row in old_skill}
                new_inputs = {output_identity(Path(row["output"]))[0] for row in new_skill}
                common = old_inputs & new_inputs
                lines.append(f"- {engine} (common inputs: {len(common)})")
                metrics = ["hard_fail", "human_likeness"]
                if old_skill and new_skill and any("naturalness" in row.get("verdict", {}) for row in old_skill) and \
                        any("naturalness" in row.get("verdict", {}) for row in new_skill):
                    metrics.append("naturalness")
                for metric in metrics:
                    old = [row for row in old_skill if output_identity(Path(row["output"]))[0] in common and "error" not in row.get("verdict", {})]
                    new = [row for row in new_skill if output_identity(Path(row["output"]))[0] in common and "error" not in row.get("verdict", {})]
                    if metric == "hard_fail":
                        old_values, new_values = [int(_hard_fail(row)) for row in old], [int(_hard_fail(row)) for row in new]
                        old_rate = sum(old_values) / len(old_values) if old_values else None
                        new_rate = sum(new_values) / len(new_values) if new_values else None
                        lines.append(f"  - hard_fail: {old_rate:.3f} (n={len(old_values)}) -> "
                                     f"{new_rate:.3f} (n={len(new_values)})" if old_rate is not None and new_rate is not None
                                     else "  - hard_fail: n/a")
                        continue
                    else:
                        old_values = [row["verdict"][metric] for row in old if metric in row.get("verdict", {})]
                        new_values = [row["verdict"][metric] for row in new if metric in row.get("verdict", {})]
                    old_mean = sum(old_values) / len(old_values) if old_values else None
                    new_mean = sum(new_values) / len(new_values) if new_values else None
                    lines.append(f"  - {metric}: {old_mean if old_mean is not None else 'n/a'} -> {new_mean if new_mean is not None else 'n/a'}")
    report_text = "\n".join(lines) + "\n"
    (round_dir / "report.md").write_text(report_text, encoding="utf-8")
    print(report_text, end="")
    return 0


def main() -> None:
    """Parse the evaluation loop commands."""
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
    run_parser.add_argument("--with-plain", action="store_true",
                            help="also generate plain baseline outputs after round 1")
    run_parser.add_argument("--samples", type=int, default=1,
                            help="outputs to generate per input and condition")
    run_parser.set_defaults(handler=run)
    judge_parser = commands.add_parser("judge")
    common(judge_parser)
    judge_parser.add_argument("--judge-engine", default="claude")
    judge_parser.add_argument("--judge-model", default="claude-opus-5-5")
    judge_parser.add_argument("--jobs", type=int, default=4)
    judge_parser.set_defaults(handler=judge)
    pair_parser = commands.add_parser("pair")
    common(pair_parser)
    pair_parser.add_argument("--judge-engine", default="claude")
    pair_parser.add_argument("--judge-model", default="claude-opus-5-5")
    pair_parser.add_argument("--all-samples", action="store_true",
                             help="compare every skill sample with plain sample 1")
    pair_parser.set_defaults(handler=pair)
    stats_parser = commands.add_parser("stats")
    common(stats_parser)
    stats_parser.add_argument("--human", help="human reference directory (default: ~/.humanizer-kr/samples)")
    stats_parser.set_defaults(handler=stats)
    pick_parser = commands.add_parser("pick")
    common(pick_parser)
    pick_parser.add_argument("--n", type=int, default=10)
    pick_parser.add_argument("--seed", type=int)
    pick_parser.add_argument("--engines", default="codex,claude")
    pick_parser.set_defaults(handler=pick)
    report_parser = commands.add_parser("report")
    common(report_parser)
    report_parser.add_argument("--human", help="human reference directory (default: ~/.humanizer-kr/samples)")
    report_parser.set_defaults(handler=report)
    args = parser.parse_args()
    raise SystemExit(args.handler(args))


if __name__ == "__main__":
    main()

