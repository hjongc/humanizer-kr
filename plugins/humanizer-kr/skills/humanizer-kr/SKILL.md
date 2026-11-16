---
name: humanizer-kr
description: Rewrite, edit, or review Korean text so it sounds natural, human, and source-grounded rather than AI-generated or translation-like. Use for Korean product copy, posts, emails, public notices, documentation, essays, proposals, scripts, and other drafts that need Korean-specific register control, plain-language discipline, removal of AI-writing tells, or voice matching from a user sample or saved voice profile.
---

# Humanizer KR

Use this skill to make Korean writing sound like it was written by a person who understands the audience, not by a chatbot translating an English outline.

Do not help users hide plagiarism, impersonate a real person's authorship, or bypass academic or hiring integrity checks. It is fine to improve clarity, register, voice, and readability when the user owns or is allowed to edit the text.

## Core Workflow

1. Identify the genre and reader: product copy, public notice, email, essay, documentation, proposal, social post, or spoken script.
2. Preserve facts, intent, paragraph coverage, and constraints. Rewrite the language, not the underlying claims.
3. Look for `voice.md` in `./.humanizer-kr/` first, then `~/.humanizer-kr/`; load only that profile during a rewrite.
4. Choose one register and keep it stable:
   - formal public/professional: `합니다`, `하십시오`
   - polite product/support: `해요`, `해주세요`
   - concise internal note: plain declarative Korean with minimal honorific padding
5. Rewrite AI-like wording into Korean that is concrete, direct, and rhythmically varied.
6. Run the Korean audit pass before returning the final answer.
7. Run one naturalness pass: check whether the rewrite still feels flat, generic, vague, or mismatched to the genre; check it against sourced rules (S and N) at the strength required for the genre.

When factual claims are weak, do not invent supporting detail. Either keep the claim modest, mark the uncertainty, or ask for a source when the source materially affects the rewrite.

## Naturalness Rubric

Use this after removing obvious AI-writing tells. A rewrite can be clean and still feel unnatural.

- Genre fit: product copy should be sharper than documentation; support email should tell the reader what to do next; public notices should separate issue, affected reader, action, and timing when those facts exist.
- Reader action: if the reader needs to do something, name the action. Avoid vague endings such as `필요한 조치를 진행해 주세요` unless the source genuinely withholds the action.
- Concrete subject: prefer the actual actor or object over generic `이 도구`, `이 서비스`, `본 기능` when the source gives enough context.
- Rhythm: vary sentence length. Do not make every sentence land with the same `합니다` rhythm unless the genre requires formal uniformity.
- Warmth: remove ceremonial padding, but do not make support or public-facing text cold. Keep enough respect for the reader relationship.
- Claim control: do not add benefits, examples, numbers, deadlines, app names, institutions, or causal claims that the source did not provide.
- Voice match: use a sample or saved profile over generic polished Korean.

When the first rewrite is safe but bland, improve once more. Prefer a smaller, more specific sentence over a broader sentence with polished wording.

## Failure and Uncertainty Policy

Fail visible when the source is too thin to rewrite safely.

- If an action, timeline, affected audience, or cause is missing from a notice or support reply, do not invent it. Keep the final text modest and add a short note asking for the missing detail.
- If a claim needs evidence, do not dress it up. Lower the claim or ask for the source.
- If the requested voice conflicts with facts, legal wording, quoted text, or safety constraints, preserve the constraint and explain the tradeoff briefly.
- If the user asks for an integrity-bypassing rewrite, refuse that use and offer a clarity/readability edit that does not misrepresent authorship.

## Voice Calibration

If the user provides a Korean writing sample, read it before editing and match:

- sentence length and paragraph rhythm
- ending style (`-다`, `-합니다`, `-해요`, mixed casual)
- common connectors and how often they appear
- tolerance for English terms, parentheses, slashes, and emoji
- level of emotional color, humor, or bluntness

Do not "upgrade" the user's voice into generic polished Korean. If the sample is plain, stay plain. If the sample is slightly rough but intentional, keep that pulse.

### Saved voice profile

Before rewriting, look for `voice.md` in `./.humanizer-kr/` (project), then `~/.humanizer-kr/` (personal). Use the first one found. If neither exists, proceed as today; when the user supplies a sample, mention profile setup in at most one line and never ask them to create one unprompted. Each voice directory holds the derived `voice.md` and a `samples/` directory with one raw sample per `NN-<genre>.md` file (for example, `01-work-email.md`). Never store samples inside the installed skill directory, which plugin updates replace.

Precedence: explicit instructions in the current request > a sample pasted in the current request > saved profile > this skill's generic defaults. Facts, quoted text, legal wording, and a required public register (such as a public notice) still take priority over the profile. Keep the constraint and say so briefly when they conflict.

The profile changes voice only. It never licenses adding facts, anecdotes, or personal experience, and it does not disable the audit pass. If the profile explicitly allows an expression flagged by the tells list (for example, the user really writes `솔직히`), follow the profile for that expression.

When the user asks to save or learn their style (for example, `내 문체 저장해줘` or "set up my voice"), one sample is enough to start; more samples and genres improve the profile. Save each pasted sample verbatim as its own file under `samples/` in `~/.humanizer-kr/` by default. Use `./.humanizer-kr/` only if the user asks for project storage. Then read the saved files, extract a profile using `references/voice-profile-template.md`, write it to that directory's `voice.md`, and show the resulting profile. Saving on this request needs no second confirmation. When adding samples later, save the new files and re-extract the profile from all files in `samples/`. Extract register and endings; sentence construction (length, openings, clause chaining, subject omission, typical endings); paragraph construction (length, whether conclusion or context comes first, connections, and closings); connectors; vocabulary and tolerance for English terms; punctuation and emoji; and emotional color. Describe only what the samples show; mark any field `not enough evidence` instead of guessing. Since samples are stored as pasted, tell the user in one line where they were saved. For project storage, suggest adding `.humanizer-kr/` to `.gitignore`. Keep names, contacts, and other personal data out of `voice.md`. Read `samples/` only to build or rebuild the profile, or when the user asks to check a rewrite against the originals; normal rewrites load only `voice.md`.

When a correction reveals a lasting preference (for example, `나는 이런 말 안 써`), offer to add one line to the profile's do/avoid lists. Never edit the profile silently.

A profile describes the user's own voice. Do not build one to imitate another real person's authorship, consistent with the refusal policy above.

## Korean AI-Writing Tells

These tells are tier H heuristics without an official source; where a tell overlaps an S-rule, the S-rule is the basis. Look for clusters, not isolated words. The five groups below are the editing frame; the 20 patterns are observation signals, not banned words. Apply them after identifying the genre, reader, and register.

Read `references/rewriting-playbook.md` when a rewrite needs a concrete edit strategy or when the first pass is safe but still bland. Do not promote a new tell into the main workflow until it has evidence, a clean negative example, and regression coverage.

### 1. Evidence and Claim Strength

Fix sentences where the claim is larger than the evidence. Lower broad claims into verified facts, specific actions, conditions, or explicit uncertainty.

- Inflated praise: when `혁신적인`, `최적화된`, `강력한`, or similar praise appears before evidence, replace it with the actual feature, result, or behavior.
- Vague authority: when `많은 전문가들은`, `업계에서는`, or `여러 연구에 따르면` lacks a source, add a specific source, narrow the claim, or remove the authority frame.
- Knowledge-gap disclaimer: when `정보는 제한적이지만` or `알려진 바는 많지 않지만` leads into speculation, separate what is known from what is unknown.
- Generic positive conclusion: replace `앞으로의 행보가 기대됩니다` or `좋은 결과가 기대됩니다` with a known next step, plan, or modest close.
- Hedging stack: when `상당히`, `비교적`, `~로 보입니다`, and `~할 수 있을 것으로 예상됩니다` pile up, keep the strongest claim the evidence supports.

Before: `다음 업데이트에서 검색 필터와 저장 기능을 먼저 개선하며 앞으로의 행보가 기대됩니다.`
After: `다음 업데이트에서는 검색 필터와 저장 기능을 먼저 개선합니다.`

### 2. Translationese and Vocabulary Density

Fix wording that sounds like a translated outline or business-English draft. Prefer Korean relationships, natural collocations, and terms the reader actually uses.

- Translationese connectors: when `또한`, `이를 통해`, `더 나아가`, `결과적으로`, or `전반적으로` repeats, remove the signpost or name the real relationship.
- English-first wording: replace `인사이트`, `니즈`, `밸류`, `퍼포먼스`, `어프로치`, or `커뮤니케이션` only when a clearer Korean term fits the reader; also reduce stiff abstract wording when it hides the action.
- Synonym cycling: when `사용자`, `고객`, `이용자`, and `클라이언트` refer to the same person, keep the clearest term consistent.

Before: `또한, 이를 통해 사용자는 필요한 정보를 더 빠르게 찾고 헤매는 시간을 줄일 수 있습니다.`
After: `사용자는 필요한 정보를 더 빨리 찾고 덜 헤맵니다.`

### 3. Actors and Verbs

Fix sentences where action disappears into nouns, passive endings, or vague availability claims. Make the actor and verb visible when the genre allows it.

- Nominalized Korean: turn chains of `-화`, `-성`, `-적`, `것`, `부분`, `측면`, `기반으로`, or `중심으로` into verbs and concrete subjects.
- Passive or availability chains: when `제공됩니다`, `진행됩니다`, `확인됩니다`, `가능합니다`, `저장됩니다`, or `처리됩니다` repeats, name who or what acts.

Before: `반복 업무 효율성 향상을 위한 자동화 기능 제공이 가능합니다.`
After: `반복 업무를 자동으로 처리해 시간을 줄입니다.`

### 4. Register and Relationship

Fix the relationship with the reader before polishing individual words. Keep respect, but remove ceremonial padding and empty friendliness.

- Register drift: do not mix `합니다`, `해요`, and `해야 한다` unless the source voice clearly does so on purpose.
- Chatbot artifacts: cut `물론입니다`, `좋은 질문입니다`, `아래와 같이 정리해 드립니다`, and similar assistant scaffolding unless drafting a chat reply.
- Honorific padding: simplify `사용자님께서는`, `확인하시어`, `참고 부탁드립니다`, and `이용에 참고하여 주시기 바랍니다` while keeping polite intent.
- Sycophantic or fake-candid openers: remove `정확히 보셨습니다`, `솔직히 말하면`, `사실은`, or `핵심은` when they add drama without content.

Before: `사용자님께서는 아래 내용을 확인하시어 이용에 참고 부탁드립니다.`
After: `아래 내용을 확인해 주세요.`

### 5. Structure and Rhythm

Fix formulaic structure only when it makes the text less useful. Lists, labels, and slogans are allowed when the genre needs them; otherwise keep the shape simple.

- Over-structured chatbot formatting: reduce forced groups of three, generic `핵심 요약` or `기대 효과` sections, and label-heavy summaries when they do not aid scanning.
- Punctuation and parenthesis clutter: split sentences packed with parentheses, slash pairs, decorative quotes, arrows, or repeated colons.
- Heading warm-ups: let headings do their job; cut `살펴보겠습니다`, `알아보겠습니다`, and `다음과 같습니다` when they only repeat the heading.
- Bold-label lists: replace repeated `**라벨:** 설명` bullets with normal bullets, a table, or prose unless label-heavy scanning is needed.
- Change-anchored documentation: describe the current behavior instead of `새롭게 추가된`, `개선되었습니다`, or `변경되었습니다`, except in changelogs or migration guides.
- Uniform cadence and slogan rhythm: vary sentence length when every sentence lands like `빠릅니다. 간단합니다. 강력합니다.`

Before: `## 설정\n설정 방법을 살펴보겠습니다.\n알림을 끄려면 설정에서 알림 옵션을 해제합니다.`
After: `## 설정\n알림을 끄려면 설정에서 알림 옵션을 해제합니다.`

## Source-Grounded Korean

Read `references/korean-source-rules.md` when:

- correcting public-facing Korean
- choosing between a loanword and a Korean alternative
- checking standard wording, refined terms, or foreign-word spelling
- explaining why a Korean phrase sounds awkward
- building evaluation criteria for Korean writing quality

Do not cite these sources mechanically in ordinary rewrites. Cite them only when the user asks for rationale, source basis, or style rules.

Sourced rules (S and N) and their source pages are in `references/korean-source-rules.md`. Apply them at the strength set by its genre matrix; cite the rule ID and source only when the user asks for rationale.

## Optional Audit Script

For file-based review, run:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py <file>
```

Use the script as a smoke test, not as the final judge. It flags patterns that deserve attention; it does not prove a text is AI-generated.

For a second quality pass, run:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py --quality --genre product-copy <file>
```

Use `--quality` to look for bland-but-clean output, weak reader actions, leftover availability phrasing, and genre mismatch.

For a release-style gate over the public examples, run:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py --after-examples
```

Public after examples are regression fixtures. Keep `examples/*.after.ko.md` clean under the basic audit and the genre-specific quality pass unless a future test explicitly documents why a pattern is allowed.

## Output

If the user asks to rewrite, return the final rewritten text first. Add a short note only when tradeoffs matter, such as a changed register, removed unsupported claims, missing source details, or preserved technical terms.

If the user asks for a stronger result or an improvement loop, return:

1. final rewrite
2. what changed from the first safe rewrite
3. any missing detail that would make the result more specific

If the user asks to review, return:

1. the strongest Korean AI-writing tells found
2. the likely audience/register problem
3. a rewritten version or targeted edits

Never add facts, examples, numbers, institutions, citations, or personal experience unless they are present in the source text or supplied by the user.
