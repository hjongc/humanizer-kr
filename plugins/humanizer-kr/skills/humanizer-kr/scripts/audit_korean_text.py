#!/usr/bin/env python3
"""Flag Korean AI-writing tells for review.

This script is intentionally conservative: it reports patterns that may deserve
editing, but it never labels a text as AI-generated.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    code: str
    label: str
    pattern: re.Pattern[str]
    advice: str


RULES = [
    Rule(
        "translationese-connectors",
        "translation-like connector",
        re.compile(r"(또한|더 나아가|이를 통해|나아가|결과적으로|전반적으로|궁극적으로|이러한 점에서)"),
        "Cut the signpost or name the real relationship between sentences.",
    ),
    Rule(
        "inflated-praise",
        "inflated praise",
        re.compile(r"(혁신적|획기적|차별화된|몰입감 있는|탁월한|최적화된|강력한|완벽한|풍부한|새로운 가능성)"),
        "Replace broad praise with concrete evidence or a smaller claim.",
    ),
    Rule(
        "nominalization",
        "nominalized wording",
        re.compile(r"(\w+(?:화|성|적)\b|부분|측면|과정|기반으로|중심으로|것입니다|있도록)"),
        "Prefer active verbs and concrete subjects.",
    ),
    Rule(
        "passive-chain",
        "passive or availability chain",
        re.compile(r"(제공됩니다|진행됩니다|확인됩니다|가능합니다|기대됩니다|구성됩니다|저장됩니다|처리됩니다)"),
        "Name the actor or switch to a direct verb.",
    ),
    Rule(
        "vague-authority",
        "vague authority",
        re.compile(r"(많은 전문가|업계에서는|여러 연구에 따르면|사용자들은 원합니다|대부분의 사람들은|일각에서는)"),
        "Add a specific source, narrow the claim, or remove the authority framing.",
    ),
    Rule(
        "chatbot-artifact",
        "chatbot artifact",
        re.compile(r"(물론입니다|좋은 질문입니다|아래와 같이 정리|도움이 되었으면|필요하시면.*도와)"),
        "Remove assistant scaffolding unless the text is a direct chat reply.",
    ),
    Rule(
        "business-english",
        "business-English dependency",
        re.compile(r"(인사이트|임팩트|니즈|밸류|퍼포먼스|이슈|딜리버리|온보딩|서드 파티|플랜 B)"),
        "Keep only if the audience expects the term; otherwise use clearer Korean.",
    ),
]


def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def audit(text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for rule in RULES:
        for match in rule.pattern.finditer(text):
            findings.append(
                {
                    "code": rule.code,
                    "label": rule.label,
                    "line": line_number(text, match.start()),
                    "match": match.group(0),
                    "advice": rule.advice,
                }
            )

    endings = re.findall(r"습니다[.?!]?|니다[.?!]?", text)
    if len(endings) >= 8:
        findings.append(
            {
                "code": "repetitive-formal-endings",
                "label": "repetitive formal endings",
                "line": None,
                "match": f"{len(endings)} formal endings",
                "advice": "Vary sentence length and structure if the genre allows it.",
            }
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Korean text for AI-writing tells.")
    parser.add_argument("path", nargs="?", help="UTF-8 text or Markdown file. Reads stdin when omitted.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    text = read_input(args.path)
    findings = audit(text)

    if args.json:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
        return 0

    if not findings:
        print("No obvious Korean AI-writing tells found.")
        return 0

    for item in findings:
        line = f"line {item['line']}" if item["line"] else "whole text"
        print(f"- [{item['code']}] {line}: {item['match']}")
        print(f"  {item['advice']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
