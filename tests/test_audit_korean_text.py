#!/usr/bin/env python3
"""Regression tests for the Humanizer KR audit helper."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "humanizer-kr" / "scripts" / "audit_korean_text.py"

spec = importlib.util.spec_from_file_location("audit_korean_text", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def codes(text: str) -> set[str]:
    return {item["code"] for item in module.audit(text)}


def quality_codes(text: str, genre: str = "general") -> set[str]:
    return {item["code"] for item in module.quality_review(text, genre)}


AFTER_EXAMPLE_GENRES = {
    "product-copy.after.ko.md": "product-copy",
    "public-notice.after.ko.md": "public-notice",
    "support-email.after.ko.md": "support-email",
    "proposal.after.ko.md": "proposal",
    "docs.after.ko.md": "docs",
    "social-post.after.ko.md": "social-post",
}

BLOCKED_AFTER_PHRASES = [
    "혁신적인",
    "최적화된",
    "이를 통해",
    "참고 부탁드립니다",
    "앞으로의 행보가 기대됩니다",
    "아래와 같이 정리",
    "좋은 질문입니다",
]


class AuditKoreanTextTests(unittest.TestCase):
    def test_flags_translationese_and_inflated_praise(self) -> None:
        found = codes("또한 본 솔루션은 혁신적인 경험을 제공합니다. 이를 통해 생산성이 향상됩니다.")
        self.assertIn("translationese-connectors", found)
        self.assertIn("inflated-praise", found)

    def test_does_not_label_plain_text_as_ai_generated(self) -> None:
        findings = module.audit("서비스 이용 중 문제가 발생할 수 있습니다. 아래 내용을 확인하십시오.")
        self.assertEqual(findings, [])

    def test_repetitive_formal_endings_threshold(self) -> None:
        text = " ".join(["확인합니다." for _ in range(8)])
        found = codes(text)
        self.assertIn("repetitive-formal-endings", found)

    def test_flags_service_copy_padding_and_business_english(self) -> None:
        found = codes("사용자님께서는 아래 내용을 확인하시어 이슈 해결에 참고 부탁드립니다.")
        self.assertIn("honorific-padding", found)
        self.assertIn("business-english", found)

    def test_flags_structured_chatbot_formatting(self) -> None:
        text = "- **속도:** 속도가 개선되었습니다.\n사용 방법을 살펴보겠습니다."
        found = codes(text)
        self.assertIn("bold-label-list", found)
        self.assertIn("heading-warmup", found)
        self.assertIn("change-anchored-doc", found)

    def test_flags_register_drift_and_synonym_cycling(self) -> None:
        text = "사용자는 설정을 저장합니다. 고객은 결과를 확인해요. 이용자는 알림을 받는다."
        found = codes(text)
        self.assertIn("register-drift", found)
        self.assertIn("synonym-cycling", found)

    def test_flags_speculative_filler_and_generic_close(self) -> None:
        text = "구체적인 정보는 제한적이지만 상당히 긍정적인 영향을 줄 수 있을 것으로 보입니다. 앞으로의 행보가 기대됩니다."
        found = codes(text)
        self.assertIn("knowledge-gap-disclaimer", found)
        self.assertIn("hedging-stack", found)
        self.assertIn("generic-positive-conclusion", found)

    def test_flags_punctuation_clutter_and_slogan_rhythm(self) -> None:
        text = "본 기능은 사용자(관리자/운영자)의 업무 효율을 높입니다. 빠릅니다. 간단합니다. 강력합니다."
        found = codes(text)
        self.assertIn("punctuation-clutter", found)
        self.assertIn("slogan-rhythm", found)

    def test_quality_review_flags_clean_but_flat_product_copy(self) -> None:
        text = "이 도구는 어색한 표현을 더 자연스러운 한국어로 바꿉니다. 문장의 톤을 맞출 수 있습니다."
        found = quality_codes(text, "product-copy")
        self.assertIn("generic-subject", found)
        self.assertIn("safe-but-flat", found)

    def test_quality_review_flags_weak_notice_action(self) -> None:
        text = "서비스 이용 중 문제가 발생할 수 있습니다. 아래 내용을 확인한 뒤 필요한 조치를 진행해 주세요."
        found = quality_codes(text, "public-notice")
        self.assertIn("weak-reader-action", found)
        self.assertIn("ceremonial-notice", found)

    def test_quality_review_accepts_specific_support_reply(self) -> None:
        text = "알림은 설정 메뉴에서 끌 수 있습니다. 같은 문제가 계속되면 오류 화면을 보내 주세요."
        findings = module.quality_review(text, "support-email")
        self.assertEqual(findings, [])

    def test_public_after_examples_avoid_blocked_ai_tells(self) -> None:
        for name in AFTER_EXAMPLE_GENRES:
            with self.subTest(example=name):
                text = (ROOT / "examples" / name).read_text(encoding="utf-8")
                for phrase in BLOCKED_AFTER_PHRASES:
                    self.assertNotIn(phrase, text)

    def test_public_after_examples_pass_basic_audit(self) -> None:
        for name in AFTER_EXAMPLE_GENRES:
            with self.subTest(example=name):
                text = (ROOT / "examples" / name).read_text(encoding="utf-8")
                findings = module.audit(text)
                self.assertEqual(findings, [])

    def test_public_after_examples_pass_genre_quality_review(self) -> None:
        for name, genre in AFTER_EXAMPLE_GENRES.items():
            with self.subTest(example=name, genre=genre):
                text = (ROOT / "examples" / name).read_text(encoding="utf-8")
                findings = module.quality_review(text, genre)
                self.assertEqual(findings, [])

    def test_after_examples_gate_passes_public_examples(self) -> None:
        results = module.audit_after_examples(ROOT / "examples")
        self.assertTrue(results)
        self.assertTrue(all(not item["findings"] and not item["quality_findings"] for item in results))

    def test_fail_on_findings_returns_nonzero_for_cli_gate(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--fail-on-findings",
            ],
            input="또한 혁신적인 기능을 제공합니다.",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("translationese-connectors", result.stdout)


if __name__ == "__main__":
    unittest.main()
