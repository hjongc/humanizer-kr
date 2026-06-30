#!/usr/bin/env python3
"""Regression tests for the Humanizer KR audit helper."""

from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
