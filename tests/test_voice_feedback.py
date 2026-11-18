"""Regression tests for local voice feedback persistence and undo."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "skills/humanizer-kr/scripts/voice_feedback.py"
SPEC = importlib.util.spec_from_file_location("voice_feedback", SCRIPT)
feedback = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(feedback)
PROFILE = "# Voice Profile\n\n## Observed Features\nKeep these observations.\n\n## Explicit User Preferences\n\n- Do: keep technical terms.\n\n## Per-Genre Application\nKeep this section.\n"


class VoiceFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / ".humanizer-kr"
        self.directory.mkdir()
        self.profile = self.directory / "voice.md"
        self.profile.write_text(PROFILE, encoding="utf-8")

    def payload(self, **values):
        return {"expected_profile_sha256": feedback.digest(self.profile.read_bytes()), **values}

    def test_active_directory_precedence_and_explicit_override(self):
        project = Path(self.temp.name)
        home = project / "home"
        personal = home / ".humanizer-kr"
        personal.mkdir(parents=True)
        (personal / "voice.md").write_text("personal")
        self.assertEqual(feedback.resolve_directory(project, home), self.directory)
        self.assertEqual(feedback.resolve_directory(project, home, personal), personal)
        self.profile.unlink()
        self.assertEqual(feedback.resolve_directory(project, home), personal)
        with self.assertRaisesRegex(ValueError, "No voice.md"):
            feedback.resolve_directory(project, home, project / "missing")

    def test_preference_replacement_preserves_other_profile_sections_and_undo(self):
        first = feedback.record_feedback(self.directory, self.payload(preference="짧은 문장을 선호한다.", reason="Explicit user request"))
        current = self.profile.read_text()
        self.assertIn("- User preference: 짧은 문장을 선호한다.", current)
        self.assertIn("Keep these observations.", current)
        self.assertIn("Keep this section.", current)
        second = feedback.record_feedback(self.directory, self.payload(preference="설명문에서는 긴 문장도 허용한다.", replace=["- User preference: 짧은 문장을 선호한다."]))
        self.assertNotIn("- User preference: 짧은 문장을 선호한다.", self.profile.read_text())
        self.assertIn("- Do: keep technical terms.", self.profile.read_text())
        self.assertEqual(feedback.undo(self.directory)["target_id"], second["id"])
        self.assertEqual(self.profile.read_text(), current)
        self.assertEqual(feedback.undo(self.directory)["target_id"], first["id"])
        self.assertEqual(self.profile.read_text(), PROFILE)
        with self.assertRaisesRegex(ValueError, "No active"):
            feedback.undo(self.directory)

    def test_correction_choice_and_missing_reason_do_not_infer_rules(self):
        before = self.profile.read_bytes()
        record = feedback.record_feedback(self.directory, self.payload(before="삭제할 문장이다.", after="", choice="neither", scope="trial-1"))
        self.assertFalse(record["profile_changed"])
        self.assertEqual(record["feedback"]["after"], "")
        self.assertNotIn("reason", record["feedback"])
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertFalse((self.directory / "analysis/voice-feedback-backups").exists())
        with self.assertRaisesRegex(ValueError, "No active"):
            feedback.undo(self.directory)

    def test_undo_refuses_newer_manual_edits_and_corrupt_backups(self):
        record = feedback.record_feedback(self.directory, self.payload(preference="Keep connectors."))
        after = self.profile.read_bytes()
        self.profile.write_text("New manual preference")
        with self.assertRaisesRegex(ValueError, "newer edits"):
            feedback.undo(self.directory)
        self.assertEqual(self.profile.read_text(), "New manual preference")
        self.profile.write_bytes(after)
        backup = self.directory / "analysis/voice-feedback-backups" / (record["id"] + ".md")
        backup.write_text("corrupted")
        with self.assertRaisesRegex(ValueError, "Backup hash"):
            feedback.undo(self.directory)
        self.assertEqual(self.profile.read_bytes(), after)

    def test_invalid_and_stale_feedback_cannot_mutate_profile(self):
        payloads = [self.payload(before="only before"), self.payload(choice="unknown"),
                    self.payload(replace=["- Do: keep technical terms."]), self.payload(preference="short", surprise=True),
                    self.payload(preference="short", expected_profile_sha256="0" * 64),
                    self.payload(preference="short", replace=["- not an existing preference"])]
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                feedback.record_feedback(self.directory, payload)
            self.assertEqual(self.profile.read_text(), PROFILE)
            self.assertFalse((self.directory / ".feedback.lock").exists())

    def test_history_write_failure_rolls_back_record_and_undo(self):
        with patch.object(feedback, "append_record", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                feedback.record_feedback(self.directory, self.payload(preference="short"))
        self.assertEqual(self.profile.read_text(), PROFILE)
        feedback.record_feedback(self.directory, self.payload(preference="short"))
        after = self.profile.read_bytes()
        with patch.object(feedback, "append_record", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                feedback.undo(self.directory)
        self.assertEqual(self.profile.read_bytes(), after)

    def test_lock_prevents_overlapping_writer_without_deleting_existing_lock(self):
        lock = self.directory / ".feedback.lock"
        lock.write_text("1234")
        with self.assertRaisesRegex(ValueError, "already being updated"):
            feedback.record_feedback(self.directory, self.payload(preference="short"))
        self.assertEqual(self.profile.read_text(), PROFILE)
        self.assertEqual(lock.read_text(), "1234")

    def test_record_without_preferences_section_and_duplicate_preference(self):
        self.profile.write_text("# Voice Profile\n\nExisting observations.\n")
        feedback.record_feedback(self.directory, self.payload(preference="Keep connectors."))
        record = feedback.record_feedback(self.directory, self.payload(preference="Keep connectors."))
        self.assertFalse(record["profile_changed"])
        self.assertEqual(self.profile.read_text().count("- User preference: Keep connectors."), 1)

    def test_corrupt_history_is_rejected_before_modification(self):
        log = self.directory / "analysis/voice-feedback.jsonl"
        log.parent.mkdir()
        for value in ('not json\n', '{"operation":"undo","id":123}\n'):
            log.write_text(value)
            with self.assertRaises(ValueError):
                feedback.record_feedback(self.directory, self.payload(preference="short"))
            self.assertEqual(self.profile.read_text(), PROFILE)

    def test_windows_line_endings_and_ambiguous_sections(self):
        original = PROFILE.replace("\n", "\r\n").encode()
        self.profile.write_bytes(original)
        feedback.record_feedback(self.directory, self.payload(preference="Keep connectors."))
        updated = self.profile.read_bytes()
        self.assertEqual(updated.count(b"## Explicit User Preferences"), 1)
        self.assertNotIn(b"\r\r\n", updated)
        self.assertIn(b"\r\n- User preference: Keep connectors.", updated)
        feedback.undo(self.directory)
        self.assertEqual(self.profile.read_bytes(), original)
        self.profile.write_text(PROFILE + "\n## Explicit User Preferences\n- other\n")
        with self.assertRaisesRegex(ValueError, "Multiple explicit"):
            feedback.record_feedback(self.directory, self.payload(preference="short"))

    def test_cli_show_record_and_undo(self):
        def run(*args):
            result = subprocess.run([sys.executable, str(SCRIPT), *args, "--directory", str(self.directory)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)
        shown = run("show")
        payload = Path(self.temp.name) / "input.json"
        payload.write_text(json.dumps({"expected_profile_sha256": shown["profile_sha256"], "preference": "Keep connectors."}))
        saved = run("record", "--input", str(payload))
        self.assertTrue(saved["profile_changed"])
        self.assertEqual(run("undo")["target_id"], saved["id"])
        self.assertEqual(self.profile.read_text(), PROFILE)


if __name__ == "__main__":
    unittest.main()
