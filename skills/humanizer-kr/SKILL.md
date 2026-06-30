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

Watch unnecessary loanwords and literal translations: `인사이트`, `임팩트`, `니즈`, `밸류`, `핵심 밸류`, `퍼포먼스`, `이슈`, `딜리버리`, `온보딩`.

Use Korean alternatives when they are clearer, but do not force replacements for established technical terms. For difficult Chinese-character words or foreign words, consult `references/korean-source-rules.md`.

### 9. Punctuation and Parenthesis Clutter

Watch stacked parentheses, slash pairs, quote marks around ordinary words, and decorative punctuation. Korean text often becomes more natural when the sentence is split rather than packed.

Before: `본 기능은 사용자(관리자/운영자)의 업무 효율(생산성)을 높입니다.`
After: `이 기능은 관리자와 운영자의 반복 업무를 줄입니다.`

### 10. Chatbot Artifacts

Cut assistant scaffolding unless the user explicitly wants a reply draft:

- `물론입니다`
- `좋은 질문입니다`
- `아래와 같이 정리해 드립니다`
- `도움이 되었으면 좋겠습니다`
- `필요하시면 더 도와드리겠습니다`

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
