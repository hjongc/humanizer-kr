"""Tests for the maintainer evaluation loop."""

from __future__ import annotations

import importlib.util
import difflib
import hashlib
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
    def test_skill_prompt_excludes_saved_voice_profiles(self) -> None:
        prompt = loop.make_prompt("원문", "skill")
        self.assertTrue(prompt.startswith(loop.SKILL_PATH.read_text(encoding="utf-8") + "\n\n"))
        self.assertIn(
            "No saved voice profile applies to this task; do not look for or read voice.md.", prompt
        )

    def test_voice_run_isolated_metadata_pair_and_edit_amount(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir) / "evals"
            inputs = evals_dir / "inputs"
            inputs.mkdir(parents=True)
            source = "신청은 7일 이내입니다."
            (inputs / "docs-1.ko.md").write_text(
                f'---\ngenre: docs\nsource: generated\nmust_keep: ["7일"]\n---\n{source}',
                encoding="utf-8",
            )
            profile = Path(temporary_dir) / "private-voice.md"
            profile_text = "VOICE_PROFILE_PRIVATE: 짧고 담백한 문체를 유지합니다."
            profile.write_text(profile_text, encoding="utf-8")
            args = self.args(evals_dir, 1)
            args.conditions = "skill"
            args.voice = str(profile)
            args.samples = 2
            self.assertEqual(loop.run(args), 0)

            round_dir = evals_dir / "rounds" / "1"
            voice_output = round_dir / "outputs" / "fake" / "voice" / "docs-1.ko.md"
            self.assertTrue(voice_output.exists())
            self.assertIn("Saved voice profile (voice.md) for this writer:\n\n" + profile_text,
                          voice_output.read_text(encoding="utf-8"))
            self.assertTrue((voice_output.parent / "docs-1.ko~2.md").exists())
            self.assertTrue((round_dir / "outputs" / "fake" / "skill" / "docs-1.ko.md").exists())

            meta_path = round_dir / "meta.json"
            metadata_text = meta_path.read_text(encoding="utf-8")
            metadata = json.loads(metadata_text)
            self.assertEqual(metadata["voice_digest"], hashlib.sha256(profile.read_bytes()).hexdigest())
            self.assertNotIn(profile_text, metadata_text)
            self.assertNotIn(str(profile), metadata_text)

            args.judge_engine = "fake"
            self.assertEqual(loop.judge(args), 0)
            self.assertEqual(loop.pair(args), 0)
            pair_rows = [json.loads(line) for line in (round_dir / "pair.jsonl").read_text().splitlines()]
            self.assertIn("voice_vs_skill", {row["comparison"] for row in pair_rows})

            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
            report = (round_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## Edit amount", report)
            fake_output = voice_output.read_text(encoding="utf-8")
            similarity = difflib.SequenceMatcher(None, source, fake_output).ratio()
            length_ratio = len(fake_output) / len(source)
            self.assertIn(f"| fake/voice | {similarity:.4f} | {length_ratio:.4f} |", report)

    def test_run_rejects_missing_voice_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            args = self.args(Path(temporary_dir) / "evals", 1)
            args.conditions = "skill"
            args.voice = str(Path(temporary_dir) / "missing-voice.md")
            with self.assertRaisesRegex(ValueError, "voice profile file does not exist"):
                loop.run(args)

    def test_output_identity_accepts_single_and_numbered_samples(self) -> None:
        self.assertEqual(loop.output_identity(Path("docs-1.ko.md")), ("docs-1.ko", 1))
        self.assertEqual(loop.output_identity(Path("docs-1.ko~2.md")), ("docs-1.ko", 2))

    def test_judge_prompt_includes_both_sourced_rule_sets_and_matrix(self) -> None:
        prompt = loop.judge_prompt("public-notice", [], "원문", "결과")
        self.assertIn("## Korean AI-Writing Tells", prompt)
        self.assertNotIn("## Naturalness Rubric", prompt)
        self.assertIn("| N8 |", prompt)
        self.assertIn("## Sourced Public-Language Rules", prompt)
        self.assertIn('"rule": "S7 or N8"', prompt)
        self.assertIn("dropped_facts means verifiable content only", prompt)
        self.assertIn("Removed praise, filler, greetings, closing courtesies, and vague expectations are NOT dropped facts", prompt)
        self.assertIn("estimate turned into a promise", prompt)
        self.assertIn("requirement -> permission", prompt)
        self.assertIn('"introduced": true|false', prompt)

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

    def test_verdict_accepts_new_schema_and_filters_quotes(self) -> None:
        verdict = {"invented": [], "dropped_facts": [], "register_ok": True,
                   "ai_tells": [{"tell": "connector", "quote": "또한"},
                                {"tell": "fabricated", "quote": "없는 인용"}],
                   "human_likeness": 3, "note": "ok", "rule_violations": []}
        encoded = json.dumps(verdict)
        expected = {**verdict, "rule_violations": []}
        self.assertEqual(loop.parse_verdict(f"```json\n{encoded}\n```"), expected)
        self.assertEqual(loop.parse_verdict(f"결과: {encoded} 끝"), expected)
        verdict["rule_violations"] = [{"rule": "S8", "quote": "쓰여진 문장"},
                                      {"rule": "N8", "quote": "missing quote"}]
        verdict["ai_tells"] = [{"tell": "spacing", "quote": "쓰여진 문장"},
                               {"tell": "other", "quote": "missing quote"}]
        self.assertEqual(
            loop.parse_verdict(json.dumps(verdict), output="책에 쓰여진 문장" )["rule_violations"],
            [{"rule": "S8", "quote": "쓰여진 문장", "introduced": True}],
        )
        self.assertEqual(loop.parse_verdict(json.dumps(verdict), output="책에 쓰여진 문장")["ai_tells"],
                         [{"tell": "spacing", "quote": "쓰여진 문장"}])
        verdict["rule_violations"] = [{"rule": "N8", "quote": "위반", "introduced": False}]
        self.assertFalse(loop.parse_verdict(json.dumps(verdict))["rule_violations"][0]["introduced"])

    def test_all_inputs_parse_and_keep_facts_verbatim(self) -> None:
        for path in sorted((ROOT / "evals" / "inputs").glob("*.ko.md")):
            with self.subTest(path=path.name):
                metadata, body = loop.parse_input(path)
                self.assertIsInstance(metadata["must_keep"], list)
                for fact in metadata["must_keep"]:
                    self.assertIn(fact, body)

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
            judged_rows[0]["verdict"]["rule_violations"] = [
                {"rule": "N8", "quote": output_text[:8], "introduced": False},
                {"rule": "S8", "quote": output_text[8:16], "introduced": True},
            ]
            judge_path.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in judged_rows),
                encoding="utf-8",
            )
            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "1" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Sourced rule violations", report)
            self.assertIn("Outputs with any introduced sourced-rule violation: 1/2 (50.0%)", report)
            self.assertIn("Including inherited: 1/2 outputs with violations", report)
            self.assertIn("S8: 1", report)
            self.assertIn("N8 1, S8 1", report)
            meta = json.loads((evals_dir / "rounds" / "1" / "meta.json").read_text(encoding="utf-8"))
            self.assertRegex(meta["skill_digest"], r"^[0-9a-f]{64}$")
            self.assertIsInstance(meta["skill_dirty"], bool)
            self.assertIn("skill_sha", meta)
            (evals_dir / "inputs" / "proposal-6.ko.md").write_text(
                '---\ngenre: proposal\nsource: generated\nmust_keep: []\n---\n새 입력입니다.',
                encoding="utf-8",
            )
            args.round = 2
            args.with_plain = True
            self.assertEqual(loop.run(args), 0)
            self.assertTrue((evals_dir / "rounds" / "2" / "outputs" / "fake" / "plain" / "docs-1.ko.md").exists())
            self.assertEqual(loop.judge(args), 0)
            round_two_judge = evals_dir / "rounds" / "2" / "judge.jsonl"
            round_two_rows = [json.loads(line) for line in round_two_judge.read_text(encoding="utf-8").splitlines()]
            added_input = next(row for row in round_two_rows if "proposal-6" in row["output"] and row["condition"] == "skill")
            added_input["verdict"].update({"human_likeness": 5, "invented": ["새 사실"]})
            round_two_judge.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in round_two_rows),
                encoding="utf-8",
            )
            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "2" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Delta vs round 1", report)
            self.assertIn("common inputs: 1", report)
            self.assertIn("human_likeness: 3.0 -> 3.0", report)
            self.assertIn("hard_fail: 0.000 (n=1) -> 0.000 (n=1)", report)
            self.assertIn("Judge errors: 0", report)

    def test_run_samples_judge_and_multi_sample_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            inputs = evals_dir / "inputs"
            inputs.mkdir()
            (inputs / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: ["7일"]\n---\n신청은 7일 이내입니다.',
                encoding="utf-8",
            )
            args = self.args(evals_dir, 1)
            args.conditions = "skill"
            args.samples = 3
            self.assertEqual(loop.run(args), 0)
            output_dir = evals_dir / "rounds" / "1" / "outputs" / "fake" / "skill"
            self.assertEqual(sorted(path.name for path in output_dir.glob("*.md")),
                             ["docs-1.ko.md", "docs-1.ko~2.md", "docs-1.ko~3.md"])
            self.assertFalse((evals_dir / "rounds" / "1" / "outputs" / "fake" / "plain").exists())
            (output_dir / "docs-1.ko~2.md").write_text("resume sentinel", encoding="utf-8")
            self.assertEqual(loop.run(args), 0)
            self.assertEqual(len(list(output_dir.glob("*.md"))), 3)
            self.assertEqual((output_dir / "docs-1.ko~2.md").read_text(encoding="utf-8"), "resume sentinel")
            args.judge_engine = "fake"
            self.assertEqual(loop.judge(args), 0)
            judge_path = evals_dir / "rounds" / "1" / "judge.jsonl"
            rows = [json.loads(line) for line in judge_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(sorted(row["sample"] for row in rows), [1, 2, 3])
            rows[1]["checks"]["missing_numbers"] = ["7"]
            judge_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            with patch("builtins.print"):
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "1" / "report.md").read_text(encoding="utf-8")
            self.assertIn("hard-fail outputs 1/3", report)
            self.assertIn("Wilson 95% interval", report)
            self.assertIn("inputs failing in >= 1 sample: 1/1", report)
            self.assertIn("inputs failing in all samples: 0/1", report)

    def test_report_without_picks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            args = self.args(evals_dir, 1)
            with patch("builtins.print") as mocked_print:
                self.assertEqual(loop.report(args), 0)
            report = (evals_dir / "rounds" / "1" / "report.md").read_text(encoding="utf-8")
            self.assertIn("Human win rate: n/a (no picks)", report)
            self.assertIn("Outputs with any introduced sourced-rule violation: n/a", report)
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

    def test_pick_uses_current_round_plain_baseline_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            inputs = evals_dir / "inputs"
            inputs.mkdir()
            (evals_dir / "human").mkdir()
            (inputs / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: []\n---\n원문', encoding="utf-8"
            )
            for round_number, condition, content in (
                (1, "skill", "previous skill"),
                (2, "skill", "current skill"),
                (2, "plain", "fresh plain"),
            ):
                output = evals_dir / "rounds" / str(round_number) / "outputs" / "fake" / condition / "docs-1.ko.md"
                output.parent.mkdir(parents=True)
                output.write_text(content, encoding="utf-8")
            args = self.args(evals_dir, 2)
            args.n = 1
            with patch("builtins.input", return_value="q"), patch("builtins.print") as printed:
                loop.pick(args)
            shown = "\n".join(str(call.args[0]) for call in printed.call_args_list)
            self.assertIn("fresh plain", shown)
            self.assertNotIn("previous skill", shown)

    def test_text_stats_hand_computed_korean_example(self) -> None:
        values = loop.text_stats("---\nkind: sample\n---\n# 제목\n또한, 개선성은 빠릅니다. 사용자는 직접 합니다!")
        self.assertAlmostEqual(values["sent_len_mean"], 11.0)
        self.assertAlmostEqual(values["sent_len_cv"], 1 / 11)
        self.assertAlmostEqual(values["ending_diversity"], 0.5)
        self.assertAlmostEqual(values["connector_rate"], 0.5)
        self.assertAlmostEqual(values["nominal_rate"], 100 / 6)

    def test_pair_fake_forfeits_hard_fail_and_resumes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            inputs = evals_dir / "inputs"
            inputs.mkdir()
            (inputs / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: []\n---\n첫 원문입니다.', encoding="utf-8")
            (inputs / "docs-2.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: []\n---\n둘째 원문입니다.', encoding="utf-8")
            round_dir = evals_dir / "rounds" / "1"
            rows = []
            for name in ("docs-1.ko.md", "docs-2.ko.md"):
                for condition in ("skill", "plain"):
                    path = round_dir / "outputs" / "fake" / condition / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f"{condition} {name}", encoding="utf-8")
                    rows.append({"output": f"outputs/fake/{condition}/{name}", "engine": "fake",
                                 "condition": condition, "verdict": {"invented": ["추가 사실"]
                                 if name == "docs-1.ko.md" and condition == "skill" else [], "dropped_facts": []},
                                 "checks": {"missing_must_keep": [], "missing_numbers": []}})
            round_dir.mkdir(parents=True, exist_ok=True)
            (round_dir / "judge.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            args = self.args(evals_dir, 1)
            self.assertEqual(loop.pair(args), 0)
            pair_path = round_dir / "pair.jsonl"
            pair_rows = [json.loads(line) for line in pair_path.read_text().splitlines()]
            fail_pair = next(row for row in pair_rows if row["input"] == "docs-1.ko.md" and row["comparison"] == "skill_vs_plain")
            self.assertEqual((fail_pair["result"], fail_pair["forfeit"], fail_pair["orders"]), ("loss", True, []))
            tie_pair = next(row for row in pair_rows if row["input"] == "docs-2.ko.md" and row["comparison"] == "skill_vs_plain")
            self.assertEqual((tie_pair["result"], tie_pair["forfeit"], tie_pair["orders"]), ("tie", False, ["tie", "tie"]))
            self.assertEqual(len(pair_rows), 4)
            self.assertEqual(loop.pair(args), 0)
            self.assertEqual(len(pair_path.read_text().splitlines()), 4)

    def test_pair_all_samples_uses_plain_sample_one(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            (evals_dir / "inputs").mkdir()
            (evals_dir / "inputs" / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nsource: generated\nmust_keep: []\n---\n원문입니다.', encoding="utf-8")
            outputs = evals_dir / "rounds" / "1" / "outputs" / "fake"
            (outputs / "skill").mkdir(parents=True)
            (outputs / "plain").mkdir()
            for name, text in (("docs-1.ko.md", "skill one"), ("docs-1.ko~2.md", "skill two")):
                (outputs / "skill" / name).write_text(text, encoding="utf-8")
            (outputs / "plain" / "docs-1.ko.md").write_text("plain one", encoding="utf-8")
            args = self.args(evals_dir, 1)
            self.assertEqual(loop.pair(args), 0)
            pair_path = evals_dir / "rounds" / "1" / "pair.jsonl"
            self.assertEqual(len(pair_path.read_text(encoding="utf-8").splitlines()), 2)
            args.all_samples = True
            self.assertEqual(loop.pair(args), 0)
            rows = [json.loads(line) for line in pair_path.read_text(encoding="utf-8").splitlines()]
            second_sample = [row for row in rows if row["sample"] == 2]
            self.assertEqual(len(second_sample), 2)
            self.assertEqual({row["comparison"] for row in second_sample}, {"skill_vs_plain", "skill_vs_source"})

    def test_stats_aggregates_human_files_without_copying_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            (evals_dir / "inputs").mkdir()
            (evals_dir / "inputs" / "docs-1.ko.md").write_text(
                '---\ngenre: docs\nmust_keep: []\n---\n입력 문장입니다.', encoding="utf-8")
            human_dir = evals_dir / "private-human"
            human_dir.mkdir()
            private_sentence = "사람만 쓴 비공개 참조 문장입니다."
            (human_dir / "sample.md").write_text(private_sentence, encoding="utf-8")
            args = self.args(evals_dir, 1)
            args.human = str(human_dir)
            self.assertEqual(loop.stats(args), 0)
            saved = (evals_dir / "rounds" / "1" / "stats.json").read_text(encoding="utf-8")
            self.assertNotIn(private_sentence, saved)
            data = json.loads(saved)
            self.assertEqual(data["human"]["count"], 1)
            self.assertIn("sent_len_mean", data["human"]["mean"])

            output_dir = evals_dir / "rounds" / "1" / "outputs" / "fake" / "skill"
            output_dir.mkdir(parents=True)
            (output_dir / "docs-1.ko.md").write_text("첫 표본입니다.", encoding="utf-8")
            (output_dir / "docs-1.ko~2.md").write_text("둘째 표본입니다.", encoding="utf-8")
            values = loop.compute_stats(evals_dir, evals_dir / "rounds" / "1", None)
            self.assertEqual(values["fake/skill"]["count"], 2)

    def test_report_accepts_old_round_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            evals_dir = Path(temporary_dir)
            round_dir = evals_dir / "rounds" / "3"
            round_dir.mkdir(parents=True)
            old_row = {"output": "outputs/fake/skill/docs-1.ko.md", "engine": "fake", "condition": "skill",
                       "genre": "docs", "verdict": {"invented": [], "dropped_facts": [],
                       "register_ok": True, "reader_action_ok": True, "genre_fit": 3,
                       "naturalness": 4, "residual_tells": [], "note": "old", "rule_violations": []},
                       "checks": {"missing_must_keep": [], "missing_numbers": []},
                       "audit_before": 0, "audit_after": 0}
            (round_dir / "judge.jsonl").write_text(json.dumps(old_row) + "\n", encoding="utf-8")
            with patch("builtins.print"):
                self.assertEqual(loop.report(self.args(evals_dir, 3)), 0)
            report = (round_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## Mean naturalness", report)
            self.assertIn("## Mean genre_fit", report)
            self.assertNotIn("## Mean human_likeness", report)
            self.assertIn("- fake / skill: n/a", report)
            self.assertIn("hard-fail outputs 0/1", report)

    @staticmethod
    def args(evals_dir: Path, round_number: int):
        class Arguments:
            pass
        arguments = Arguments()
        arguments.evals_dir = str(evals_dir)
        arguments.round = round_number
        arguments.engines = "fake"
        arguments.conditions = "skill,plain"
        arguments.voice = None
        arguments.jobs = 2
        arguments.codex_model = "unused"
        arguments.claude_model = "unused"
        arguments.engine_check = False
        arguments.judge_engine = "fake"
        arguments.judge_model = "unused"
        arguments.human = None
        arguments.seed = None
        arguments.n = 1
        arguments.with_plain = False
        arguments.samples = 1
        arguments.all_samples = False
        return arguments


if __name__ == "__main__":
    unittest.main()
