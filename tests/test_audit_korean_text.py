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
        findings = module.audit("서비스 이용 중 발생할 수 있는 문제를 안내드립니다. 아래 내용을 확인해 주세요.")
        self.assertEqual(findings, [])

    def test_repetitive_formal_endings_threshold(self) -> None:
        text = " ".join(["확인합니다." for _ in range(8)])
        found = codes(text)
        self.assertIn("repetitive-formal-endings", found)


if __name__ == "__main__":
    unittest.main()
