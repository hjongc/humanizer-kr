"""Tests for the maintainer evaluation loop."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals" / "loop.py"
SPEC = importlib.util.spec_from_file_location("eval_loop", SCRIPT)
assert SPEC and SPEC.loader
loop = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop)


class EvalLoopTests(unittest.TestCase):
    def test_judge_prompt_includes_both_sourced_rule_sets_and_matrix(self) -> None:
        prompt = loop.judge_prompt("public-notice", [], "원문", "결과")
        self.assertIn("| N8 |", prompt)
        self.assertIn("| N-rules |", prompt)
        self.assertIn('"rule": "S7 or N8"', prompt)
        self.assertIn("dropped_facts means verifiable content only", prompt)
        self.assertIn("Removed praise, filler, greetings, closing courtesies, and vague expectations are NOT dropped facts", prompt)
        self.assertIn("estimate turned into a promise", prompt)

    def test_facts_accept_thousands_separator_variants(self) -> None:
        self.assertEqual(
            loop.facts("금액은 1200만 원입니다.", "금액은 1,200만 원입니다.", ["1200만 원"]),
            {"missing_must_keep": [], "missing_numbers": []},
        )

    def test_frontmatter_facts_and_thin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "draft.ko.md"
            path.write_text(
                '---\ngenre: docs\nsource: generated\nthin: true\n'
                '\nmust_keep: ["설정 > 알림", "3월 15일"]\n---\n본문 15',
                encoding="utf-8",
            )
            metadata, body = loop.parse_input(path)
        self.assertTrue(metadata["thin"])
        self.assertEqual(body, "본문 15")
        self.assertEqual(
            loop.facts("3월 15일 설정 > 알림", body, ["설정 > 알림"]),
            {"missing_must_keep": ["설정 > 알림"], "missing_numbers": ["3"]},
        )

    def test_verdict_accepts_fenced_and_embedded_json(self) -> None:
        verdict = {"invented": [], "dropped_facts": [], "register_ok": True,
                   "reader_action_ok": True, "genre_fit": 4, "naturalness": 3,
                   "residual_tells": [], "note": "ok"}
        encoded = json.dumps(verdict)
        expected = {**verdict, "rule_violations": []}
        self.assertEqual(loop.parse_verdict(f"```json\n{encoded}\n```"), expected)
        self.assertEqual(loop.parse_verdict(f"결과: {encoded} 끝"), expected)
        verdict["rule_violations"] = [{"rule": "S8", "quote": "쓰여진 문장"},
                                      {"rule": "N8", "quote": "missing quote"}]
        self.assertEqual(
            loop.parse_verdict(json.dumps(verdict), output="책에 쓰여진 문장" )["rule_violations"],
            [{"rule": "S8", "quote": "쓰여진 문장"}],
        )

    def test_fake_end_to_end_and_round_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            (evals_dir / "inputs").mkdir()
            (evals_dir / "human").mkdir()
            (evals_dir / "inputs" / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: ["7일"]\n---\n신청은 7일 이내입니다.',
                encoding="utf-8",
            )
            args = self.args(evals_dir, 1)
            self.assertEqual(loop.run(args), 0)
            args.judge_engine = "fake"
            self.assertEqual(loop.judge(args), 0)
            judge_path = evals_dir / "rounds" / "1" / "judge.jsonl"
            judged_rows = [json.loads(line) for line in judge_path.read_text(encoding="utf-8").splitlines()]
            output_text = (evals_dir / "rounds" / "1" / "outputs" / "fake" / "skill" / "docs-1.ko.md").read_text(encoding="utf-8")
            judged_rows[0]["verdict"]["rule_violations"] = [{"rule": "N8", "quote": output_text[:8]}]
            judge_path.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in judged_rows),
                encoding="utf-8",
            )
            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "1" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Sourced rule violations", report)
            self.assertIn("N8: 1", report)
            args.round = 2
            self.assertEqual(loop.run(args), 0)
            self.assertEqual(loop.judge(args), 0)
            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "2" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Delta vs round 1", report)
            self.assertIn("Judge errors: 0", report)

    def test_report_without_picks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            args = self.args(evals_dir, 1)
            with patch("builtins.print") as mocked_print:
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "1" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Human win rate: n/a (no picks)", report)
            self.assertIn("Outputs with any sourced-rule violation: n/a", report)
            mocked_print.assert_called()
            picks_path = evals_dir / "rounds" / "1" / "picks.jsonl"
            picks_path.write_text('', encoding="utf-8")
            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
                picks_path.write_text('{"seed": 17}\n', encoding="utf-8")
                self.assertEqual(loop.report(args), 0)
            self.assertIn("Human win rate: n/a (no picks)", picks_path.parent.joinpath("report.md").read_text(encoding="utf-8"))

    def test_pick_resume_reuses_seed_and_records_labels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            inputs = evals_dir / "inputs"
            inputs.mkdir()
            (evals_dir / "human").mkdir()
            (inputs / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: []\n---\n원문', encoding="utf-8"
            )
            for condition in ("skill", "plain"):
                output = evals_dir / "rounds" / "1" / "outputs" / "fake" / condition / "docs-1.ko.md"
                output.parent.mkdir(parents=True)
                output.write_text(condition, encoding="utf-8")
            args = self.args(evals_dir, 1)
            args.n = 1
            args.seed = 12
            with patch("builtins.input", return_value="a"), patch("builtins.print"):
                loop.pick(args)
            pick_path = evals_dir / "rounds" / "1" / "picks.jsonl"
            row = json.loads(pick_path.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(row["seed"], 12)
            self.assertIn(row["a_label"], {"current", "baseline"})
            self.assertIn(row["b_label"], {"current", "baseline"})
            self.assertEqual({row["a_label"], row["b_label"]}, {"current", "baseline"})
            args.seed = 999
            with patch("builtins.input", side_effect=AssertionError("already completed")), patch("builtins.print"):
                loop.pick(args)
            self.assertEqual(json.loads(pick_path.read_text().splitlines()[0])["seed"], 12)

    @staticmethod
    def args(evals_dir: Path, round_number: int):
        class Arguments:
            pass
        arguments = Arguments()
        arguments.evals_dir = str(evals_dir)
        arguments.round = round_number
        arguments.engines = "fake"
        arguments.conditions = "skill,plain"
        arguments.jobs = 2
        arguments.codex_model = "unused"
        arguments.claude_model = "unused"
        arguments.engine_check = False
        arguments.judge_engine = "fake"
        arguments.judge_model = "unused"
        arguments.seed = None
        arguments.n = 1
        return arguments


if __name__ == "__main__":
    unittest.main()
