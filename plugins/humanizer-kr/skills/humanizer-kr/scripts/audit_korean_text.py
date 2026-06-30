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
        re.compile(r"(또한|더 나아가|이를 통해|나아가|결과적으로|전반적으로|궁극적으로|이러한 점에서|이를 바탕으로|이에 따라)"),
        "Cut the signpost or name the real relationship between sentences.",
    ),
    Rule(
        "inflated-praise",
        "inflated praise",
        re.compile(r"(혁신적|획기적|차별화된|몰입감 있는|탁월한|최적화된|강력한|완벽한|풍부한|새로운 가능성|압도적|차원이 다른)"),
        "Replace broad praise with concrete evidence or a smaller claim.",
    ),
    Rule(
        "nominalization",
        "nominalized wording",
        re.compile(r"(\w+화\b|\w+적\b|효율성|생산성|가능성|안정성|확장성|편의성|중요성|필요성|방향성|전문성|부분|측면|과정|기반으로|중심으로|것입니다|있도록)"),
        "Prefer active verbs and concrete subjects.",
    ),
    Rule(
        "passive-chain",
        "passive or availability chain",
        re.compile(r"(제공됩니다|진행됩니다|확인됩니다|가능합니다|기대됩니다|구성됩니다|저장됩니다|처리됩니다|개선되었습니다|변경되었습니다|추가되었습니다)"),
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
        re.compile(r"(물론입니다|좋은 질문입니다|아래와 같이 정리|도움이 되었으면|필요하시면.*도와|맞습니다|정확히 보셨습니다)"),
        "Remove assistant scaffolding unless the text is a direct chat reply.",
    ),
    Rule(
        "business-english",
        "business-English dependency",
        re.compile(r"(인사이트|임팩트|니즈|밸류|퍼포먼스|이슈|딜리버리|온보딩|서드 파티|플랜 B|어프로치|커뮤니케이션)"),
        "Keep only if the audience expects the term; otherwise use clearer Korean.",
    ),
    Rule(
        "honorific-padding",
        "honorific padding",
        re.compile(r"(사용자님께서는|확인하시어|참고 부탁드립니다|진행 부탁드립니다|이용에 참고하여 주시기 바랍니다)"),
        "Keep respect, but remove ceremonial padding.",
    ),
    Rule(
        "knowledge-gap-disclaimer",
        "knowledge-gap disclaimer",
        re.compile(r"(구체적인 정보는 제한적이지만|알려진 바는 많지 않지만|공개된 자료에 따르면|확인된 바는 없지만|추정됩니다|가능성이 있습니다)"),
        "Say what is known, ask for a source, or cut the claim.",
    ),
    Rule(
        "generic-positive-conclusion",
        "generic positive conclusion",
        re.compile(r"(앞으로의 행보가 기대됩니다|더 나은 미래를 만들어갈 것입니다|지속적인 성장이 기대됩니다|좋은 결과를 기대할 수 있습니다|성장해 나갈 것입니다)"),
        "Replace generic optimism with a concrete next step or a modest close.",
    ),
    Rule(
        "hedging-stack",
        "stacked hedging",
        re.compile(r"(아마도|어쩌면|상당히|비교적|할 수 있을 것으로 보입니다|영향을 줄 수 있을 것으로 보입니다)"),
        "Choose the strongest claim the evidence supports.",
    ),
    Rule(
        "heading-warmup",
        "heading warm-up",
        re.compile(r"(살펴보겠습니다|알아보겠습니다|다음과 같습니다|중요합니다)"),
        "Let the heading do the setup and start with the actual content.",
    ),
    Rule(
        "bold-label-list",
        "bold-label list item",
        re.compile(r"(?m)^[^\S\n]*[-*][^\S\n]+\*\*[^*\n]{1,30}[:：]?\*\*[^\S\n]*[:：]?"),
        "Use normal bullets, a table, or prose unless label-heavy scanning is required.",
    ),
    Rule(
        "fake-candid-opener",
        "fake-candid opener",
        re.compile(r"(솔직히 말하면|사실은|핵심은|정리하면|한마디로 말하면)"),
        "Remove the theatrical opener and state the point directly.",
    ),
    Rule(
        "change-anchored-doc",
        "change-anchored documentation",
        re.compile(r"(기존 .* 대신|새롭게 추가된|개선되었습니다|변경되었습니다|추가되었습니다)"),
        "Describe the current behavior unless the text is a changelog or migration guide.",
    ),
    Rule(
        "punctuation-clutter",
        "punctuation or parenthesis clutter",
        re.compile(r"([()（）][^()（）]{0,20}[()（）]|[/→]|[\"'“”‘’][^\"'“”‘’]{1,20}[\"'“”‘’])"),
        "Split the sentence or remove decorative punctuation when it does not help the reader.",
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

    casual_endings = re.findall(r"(?:해요|돼요)[.?!]?", text)
    plain_endings = re.findall(r"(?:한다|된다|이다|있다)[.?!]?", text)
    if endings and (casual_endings or plain_endings):
        findings.append(
            {
                "code": "register-drift",
                "label": "mixed register",
                "line": None,
                "match": "mixed sentence endings",
                "advice": "Choose one reader relationship and keep the endings stable.",
            }
        )

    user_terms = re.findall(r"(사용자|고객|이용자|클라이언트)", text)
    if len(set(user_terms)) >= 3:
        findings.append(
            {
                "code": "synonym-cycling",
                "label": "synonym cycling",
                "line": None,
                "match": ", ".join(sorted(set(user_terms))),
                "advice": "Repeat the clearest term instead of rotating synonyms.",
            }
        )

    short_sentences = re.findall(r"(?<!\w)(?:빠릅니다|간단합니다|강력합니다|쉽습니다|편리합니다)[.?!]", text)
    if len(short_sentences) >= 3:
        findings.append(
            {
                "code": "slogan-rhythm",
                "label": "uniform slogan rhythm",
                "line": None,
                "match": f"{len(short_sentences)} slogan-like sentences",
                "advice": "Replace slogan rhythm with concrete details and varied sentence length.",
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
