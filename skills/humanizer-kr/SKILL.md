---
name: humanizer-kr
description: Rewrite, edit, or review Korean text so it sounds natural, human, and source-grounded rather than AI-generated or translation-like. Use for Korean product copy, posts, emails, public notices, documentation, essays, proposals, scripts, and other drafts that need Korean-specific register control, plain-language discipline, removal of AI-writing tells, or voice matching from a user-provided Korean writing sample.
---

# Humanizer KR

Use this skill to make Korean writing sound like it was written by a person who understands the audience, not by a chatbot translating an English outline.

Do not help users hide plagiarism, impersonate a real person's authorship, or bypass academic or hiring integrity checks. It is fine to improve clarity, register, voice, and readability when the user owns or is allowed to edit the text.

## Core Workflow

1. Identify the genre and reader: product copy, public notice, email, essay, documentation, proposal, social post, or spoken script.
2. Preserve facts, intent, paragraph coverage, and constraints. Rewrite the language, not the underlying claims.
3. Choose one register and keep it stable:
   - formal public/professional: `합니다`, `하십시오`
   - polite product/support: `해요`, `해주세요`
   - concise internal note: plain declarative Korean with minimal honorific padding
4. Rewrite AI-like wording into Korean that is concrete, direct, and rhythmically varied.
5. Run the Korean audit pass before returning the final answer.

When factual claims are weak, do not invent supporting detail. Either keep the claim modest, mark the uncertainty, or ask for a source when the source materially affects the rewrite.

## Voice Calibration

If the user provides a Korean writing sample, read it before editing and match:

- sentence length and paragraph rhythm
- ending style (`-다`, `-합니다`, `-해요`, mixed casual)
- common connectors and how often they appear
- tolerance for English terms, parentheses, slashes, and emoji
- level of emotional color, humor, or bluntness

Do not "upgrade" the user's voice into generic polished Korean. If the sample is plain, stay plain. If the sample is slightly rough but intentional, keep that pulse.

## Korean AI-Writing Tells

Look for clusters, not isolated words. A single `또한` or `혁신적인` is not a problem; repeated formulaic rhythm is.

### 1. Translationese Connectors

Watch: `또한`, `더 나아가`, `이를 통해`, `나아가`, `결과적으로`, `전반적으로`, `궁극적으로`, `이러한 점에서`.

Fix by removing the signpost or naming the actual relationship.

Before: `또한, 이를 통해 사용자는 더 나은 경험을 얻을 수 있습니다.`
After: `사용자는 더 빨리 찾고 덜 헤맵니다.`

### 2. Inflated Praise

Watch: `혁신적인`, `획기적인`, `차별화된`, `몰입감 있는`, `탁월한`, `최적화된`, `강력한`, `완벽한`, `풍부한`, `새로운 가능성`.

Fix with evidence or a smaller claim.

Before: `혁신적인 기능으로 최적화된 사용자 경험을 제공합니다.`
After: `검색어를 입력하면 관련 문서를 한 화면에서 비교할 수 있습니다.`

### 3. Nominalized Korean

Watch chains of `-화`, `-성`, `-적`, `-함`, `것`, `부분`, `측면`, `과정`, `기반으로`, `중심으로`.

Fix with verbs and concrete subjects.

Before: `업무 효율성 향상을 위한 자동화 기능 제공이 가능합니다.`
After: `반복 업무를 자동으로 처리해 시간을 줄입니다.`

### 4. `있습니다` and Passive Chains

Watch repeated `있습니다`, `제공됩니다`, `진행됩니다`, `확인됩니다`, `가능합니다`, `기대됩니다`.

Fix by naming the actor or switching to a direct verb.

Before: `설정 변경이 가능하며 결과는 자동으로 저장됩니다.`
After: `설정을 바꾸면 시스템이 결과를 자동으로 저장합니다.`

### 5. Vague Authority and Unsupported Claims

Watch: `많은 전문가들은`, `업계에서는`, `여러 연구에 따르면`, `사용자들은 원합니다`, `대부분의 사람들은`.

Fix with a specific source, a direct observation, or a narrower statement.

Before: `많은 전문가들은 이 방식이 중요하다고 말합니다.`
After: `이 방식은 장애가 난 지점을 로그에서 바로 확인할 때 유용합니다.`

### 6. Over-structured Chatbot Formatting

Watch bullet lists where every item starts with a bold label and colon, forced groups of three, generic sections such as `핵심 요약`, `기대 효과`, `결론`, and warm-up lines that restate the heading.

Fix by merging, cutting labels, or keeping only the list items that help scanning.

### 7. Register Drift

Watch mixed endings: `합니다` in one sentence, `해요` in the next, then `해야 한다`; or excessive honorifics such as `사용자님께서는`.

Fix by choosing one relationship with the reader and maintaining it.

### 8. English-First Word Choice

Watch unnecessary loanwords and literal translations: `인사이트`, `임팩트`, `니즈`, `밸류`, `핵심 밸류`, `퍼포먼스`, `이슈`, `딜리버리`, `온보딩`, `어프로치`, `커뮤니케이션`.

Use Korean alternatives when they are clearer, but do not force replacements for established technical terms. For difficult Chinese-character words or foreign words, consult `references/korean-source-rules.md`.

### 9. Punctuation and Parenthesis Clutter

Watch stacked parentheses, slash pairs, quote marks around ordinary words, arrows, and decorative punctuation. Korean text often becomes more natural when the sentence is split rather than packed.

Before: `본 기능은 사용자(관리자/운영자)의 업무 효율(생산성)을 높입니다.`
After: `이 기능은 관리자와 운영자의 반복 업무를 줄입니다.`

### 10. Chatbot Artifacts

Cut assistant scaffolding unless the user explicitly wants a reply draft:

- `물론입니다`
- `좋은 질문입니다`
- `아래와 같이 정리해 드립니다`
- `도움이 되었으면 좋겠습니다`
- `필요하시면 더 도와드리겠습니다`

### 11. Honorific Padding

Watch over-polite forms that make service copy sound indirect: `사용자님께서는`, `확인하시어`, `참고 부탁드립니다`, `진행 부탁드립니다`, `이용에 참고하여 주시기 바랍니다`.

Fix by keeping respect but removing ceremonial padding.

Before: `사용자님께서는 아래 내용을 확인하시어 이용에 참고 부탁드립니다.`
After: `아래 내용을 확인해 주세요.`

### 12. Knowledge-Gap Disclaimers and Speculative Filler

Watch: `구체적인 정보는 제한적이지만`, `알려진 바는 많지 않지만`, `공개된 자료에 따르면`, `추정됩니다`, `가능성이 있습니다` when the sentence then invents plausible detail.

Fix by saying what is known, asking for a source, or cutting the claim.

Before: `구체적인 정보는 제한적이지만 업계에서 중요한 역할을 한 것으로 보입니다.`
After: `현재 초안에는 역할을 확인할 근거가 없습니다.`

### 13. Generic Positive Conclusions

Watch endings such as `앞으로의 행보가 기대됩니다`, `더 나은 미래를 만들어갈 것입니다`, `지속적인 성장이 기대됩니다`, `좋은 결과를 기대할 수 있습니다`.

Fix with a concrete next step, known plan, or a modest close.

Before: `앞으로도 더 나은 경험을 제공하며 성장해 나갈 것입니다.`
After: `다음 업데이트에서는 검색 필터와 저장 기능을 먼저 개선합니다.`

### 14. Hedging Stacks

Watch stacked uncertainty: `아마도`, `어쩌면`, `일부`, `상당히`, `비교적`, `가능성이 있습니다`, `할 수 있을 것으로 보입니다`.

Fix by choosing the strongest claim the evidence supports.

Before: `상당히 긍정적인 영향을 줄 수 있을 것으로 보입니다.`
After: `반복 입력 시간을 줄일 수 있습니다.`

### 15. Heading Warm-ups

Watch headings followed by a generic one-line setup: `중요합니다`, `살펴보겠습니다`, `알아보겠습니다`, `다음과 같습니다`.

Fix by letting the heading do its job and starting with the actual content.

Before: `## 사용 방법\n사용 방법은 다음과 같습니다.\n먼저 계정을 만듭니다.`
After: `## 사용 방법\n먼저 계정을 만듭니다.`

### 16. Bold-Label Lists

Watch vertical lists where every item is `**라벨:** 설명`. This is useful in some UI specs, but in ordinary prose it often reads like chatbot output.

Fix by using normal bullets, a table, or a paragraph.

Before: `- **속도:** 속도가 개선되었습니다.`
After: `- 페이지가 더 빨리 열립니다.`

### 17. Sycophantic or Fake-Candid Openers

Watch: `좋은 질문입니다`, `맞습니다`, `정확히 보셨습니다`, `솔직히 말하면`, `사실은`, `핵심은` when used as a theatrical opener rather than content.

Fix by answering directly.

Before: `좋은 질문입니다. 핵심은 사용자가 쉽게 이해하는 것입니다.`
After: `사용자가 바로 이해할 수 있어야 합니다.`

### 18. Synonym Cycling

Watch needless variation for the same noun: `사용자`, `고객`, `이용자`, `클라이언트` all referring to the same person in one short text.

Fix by repeating the clearest term.

Before: `사용자는 설정을 저장하고, 고객은 결과를 확인하며, 이용자는 알림을 받습니다.`
After: `사용자는 설정을 저장하고 결과와 알림을 확인합니다.`

### 19. Change-Anchored Documentation

Watch docs or comments that narrate what changed instead of describing the current behavior: `기존 방식 대신`, `새롭게 추가된`, `개선되었습니다`, `변경되었습니다`.

Fix by describing the current system unless the document is a changelog or migration guide.

Before: `기존 수동 입력 방식을 개선해 자동 저장 기능이 추가되었습니다.`
After: `입력한 내용은 자동으로 저장됩니다.`

### 20. Uniform Cadence and Slogan Rhythm

Watch every sentence landing with the same length, same ending, or slogan-like fragments: `빠릅니다. 쉽습니다. 강력합니다.`

Fix with concrete detail and varied sentence length.

Before: `빠릅니다. 간단합니다. 강력합니다. 모든 팀에 적합합니다.`
After: `처음에는 기본 템플릿으로 시작하고, 팀이 자주 쓰는 항목만 나중에 추가할 수 있습니다.`

## Source-Grounded Korean

Read `references/korean-source-rules.md` when:

- correcting public-facing Korean
- choosing between a loanword and a Korean alternative
- checking standard wording, refined terms, or foreign-word spelling
- explaining why a Korean phrase sounds awkward
- building evaluation criteria for Korean writing quality

Do not cite these sources mechanically in ordinary rewrites. Cite them only when the user asks for rationale, source basis, or style rules.

## Optional Audit Script

For file-based review, run:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py <file>
```

Use the script as a smoke test, not as the final judge. It flags patterns that deserve attention; it does not prove a text is AI-generated.

## Output

If the user asks to rewrite, return the final rewritten text first. Add a short note only when tradeoffs matter, such as a changed register, removed unsupported claims, or preserved technical terms.

If the user asks to review, return:

1. the strongest Korean AI-writing tells found
2. the likely audience/register problem
3. a rewritten version or targeted edits

Never add facts, examples, numbers, institutions, citations, or personal experience unless they are present in the source text or supplied by the user.
