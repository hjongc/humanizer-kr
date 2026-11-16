# Korean Source Rules

Use this file when a Korean rewrite needs source-grounded sentence guidance.

## Source Tiers

- **A — verified Korean official primary text:** read directly; the sourced rules below are paraphrased from it.
- **B — international standard:** principles only. Do not convert rules into Korean-specific thresholds without a verified source.
- **H — heuristic AI-writing tells in `SKILL.md`:** observations from editing practice, not sourced rules. Tier H is observation, not sourced.

## Trusted Source Map

### Korean Ministry of Government Legislation (MOLEG)

**「알기 쉬운 법령 정비기준」 제10판(수정증보판)**, posted 2026-01-22
URL: https://www.moleg.go.kr/board.es?mid=a10108030000&bid=0001&act=view&list_no=146407

Use this official guide as the source for sentence rules S1–S13 below. The rules are paraphrased in our own words with page references. Since no licence type was found, reproduce only short expression pairs of a few words; do not copy statute examples or longer passages.

### Tier A — Ministry of Culture, Sports and Tourism · National Institute of Korean Language (NIKL)

**「쉬운 공공언어 쓰기 길잡이」 (2014)**  
URL: https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=208&etc_seq=399  
Licence: 공공누리 제1유형(출처표시).

Use this official guide as a source for public-language rules N1–N11 and N13 below. Rules are paraphrased with page references. Short expression pairs may be quoted with attribution.

**「(개정판) 한눈에 알아보는 공공언어 바로 쓰기」 (2022)**  
URL: https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=208&etc_seq=699  
Licence: 공공누리 제4유형(출처표시+상업적 이용금지+변경금지).

Use this guide as a source for rules N4–N6, N8, N12, and N13 below. Paraphrase only, cite page numbers, and do not reproduce its example text.

### ASD-STE100

**Tier B; known from secondary descriptions; spec not read.** Applies only to `docs` and procedural steps, at reduced strength. Use principles only: one instruction per sentence, one topic per paragraph, active voice, and consistent terms. Do not convert English word-count limits into Korean numbers. The spec is under ASD copyright; no spec text is reproduced here.

**Pending sources:** 국립국어원 「쉬운 공문서 쓰기 길잡이」 (2022, etc_seq=700; 제3유형) remains pending because its PDF text layer is mostly missing. ISO 24495-1 also remains pending. No rules below are attributed to either source.

## Sourced Sentence Rules

| ID | Rule | Source (page) | Short pair | Exception |
|---|---|---|---|---|
| S1 | Keep subject, object, and predicate; omit only what context makes obvious. | 120–121 | — | A repeated subject may be dropped. |
| S2 | Keep the subject and predicate close, and make them agree. | 120, 196 | — | — |
| S3 | Keep one topic per sentence; split long sentences and turn complex enumerations into a list. | 120, 135–147 | — | — |
| S4 | Delete duplicated, self-evident, or needless content. | 148–151 | `과반수 이상 → 과반수`; `~에 대하여 이를 → ~를` | — |
| S5 | Turn double negatives into positive statements. | 157 | — | — |
| S6 | Write the referent instead of a pointer such as `이`, `그`, or `해당` when it is not immediate. | 159 | — | — |
| S7 | Prefer active voice; name the person or organisation when it acts. | 166 | `학교법인으로부터 제출된 → 학교 법인이 제출한` | Passive voice is natural with an inanimate subject (168), as in `소멸시효가 완성된 때`. |
| S8 | Do not use double passives. | 167–168 | `쓰여진 → 쓰인`; `담겨진 → 담긴`; `구획되어진 → 구획된` | None. |
| S9 | Unpack noun strings with particles or verbs. | 170–171 | `호환성 제고를 위하여 → 호환성을 높이기 위하여` | Keep a noun string that is easy and natural (171). |
| S10 | Reduce chained `명사+의`; use `이/가` or `을/를` where they express the relationship. | 169–170 | — | — |
| S11 | Replace literal-translation phrasing with a direct Korean expression. | 170–196 | `~에 있어서 → ~에서, ~할 때`; `~을 요하는 → ~이 필요한`; `~에 한하여 → ~만`; `없는 한 → 없으면`; `~에 의하여 → ~가, ~로, ~에 따라` | Keep `~에 의하여` when it marks a cause (196). |
| S12 | Put a modifier directly before what it modifies. | 196–197 | — | — |
| S13 | Use a table, formula, or figure when it conveys the content better. | 121, 200 | — | — |

## Sourced Public-Language Rules

| ID | Rule | Source (page) | Short pair | Exception |
|---|---|---|---|---|
| N1 | Avoid commanding or authoritarian endings toward the reader. | G14 12 | `다음과 같이 작성할 것. → 다음과 같이 작성해 주십시오.`; `7일 내로 즉시 제출 바람. → 7일 내로 제출해 주십시오.` | — |
| N2 | Avoid discriminatory wording about gender, region, disability, race, ethnicity, or family form. | G14 13 | — | — |
| N3 | Spell out abbreviations and specialist terms; avoid overusing foreign words or foreign script. | G14 14–16 | — | Keep terms the intended readers already use. |
| N4 | Choose words that fit the context and make sentence parts agree. | G14 17–18; B22 11 | — | — |
| N5 | Do not over-omit sentence parts, particles, or endings. | G14 18; B22 12 | — | — |
| N6 | Keep sentences short, separate distinct information into separate sentences, and use natural word order. Neither guide sets a numeric limit. | G14 19; B22 11 | — | — |
| N7 | Use `에게` for people and `에` for organisations and things. | G14 19 | `축산 농가에게는 → 축산 농가에는` | — |
| N8 | Avoid translationese such as `~에 대해서`, `~에 의해(서) ~되다`, `~에 있어서`, `~에 있다` for `~이다`, and an inanimate or abstract subject performing a human act. | G14 20; B22 12–13 | `선정된 점포에 대해서는 → 선정된 점포에는`; `품질에 있어서 세계 최고 → 품질은 세계 최고` | — |
| N9 | When three or more nouns run together, add particles or predicates. | G14 20 | `신속대응을 위해 → 신속하게 대응하기 위해`; `적극 이용 바람 → 적극적으로 이용하기 바랍니다.` | — |
| N10 | Remove ambiguity by giving a date or count and replacing vague `및` where needed. | G14 20–21; B22 11 | `첫째 주 토요일 → 첫 번째 토요일` | — |
| N11 | Make clear whether something is required, optional, forbidden, or an exception. | G14 21 | — | — |
| N12 | Join only parallel structures with `-고`, `-며`, or `와/과`. | B22 12 | — | — |
| N13 | Put the conclusion or key point first, followed by reasons; notices state the audience, benefit or action, required documents, and contact; keep each paragraph on one connected topic. | G14 22–23; B22 13–14 | — | — |

**Overlap:** N6 ≈ S3, N8 ≈ S7/S11, N9 ≈ S9, and N12 relates to S2. When both apply, cite either rule.

## Genre Strength Matrix

**Default set — all genres:** S7, S8, S9, S10, S11, N8, and N9. These rules target translationese and noun-heavy, passive phrasing typical of machine text. N1 also applies by default to public notices and support emails.

**Opt-in set — only when the user asks for public-language or plain-language correctness:** S1–S6, S12, S13, N2–N7, and N10–N13. For public notices under this opt-in, these rules are required.

A voice profile never overrides N1, N2, or S8.

These rules were written for public language and statutes; applying all of them to casual genres makes text stiff, which is why strength varies. Applying them by default made outputs restructure and invent in our evals.

## Vocabulary and Usage Sources

These sources support word choice, spelling, and usage checks. They are not the basis of the sourced sentence and public-language rules above.

### National Institute of Korean Language public-language review

URL: https://www.korean.go.kr/front/support/supportIntro.do?mn_id=163

Use for public-facing copy, government-style notices, policy text, service messages, and any draft where clarity for general readers matters. The useful principle is easy and correct public language for ordinary readers. Apply it as a plain-language constraint: shorter sentences, explicit actors, fewer abstract nouns, and fewer unexplained technical terms.

### National Institute of Korean Language refined terms

URL: https://www.korean.go.kr/front/imprv/refineList.do?mn_id=158

Use when a draft leans on hard Chinese-character words, foreign words, or business English. Treat the refined word list as a vocabulary reference, not as a forced replacement table. Preserve established technical terms when replacing them would confuse the target reader.

Examples of the decision rule:

- `플랜 B` -> `차선책` when writing for general readers.
- `서드 파티` -> `외부 협력사` or `연계 협력사` when the context is business operations.
- Keep `API`, `SDK`, `RAG`, `로그`, or `온보딩` when the intended readers already use those terms.

### Standard Korean Dictionary

URL: https://stdict.korean.go.kr/main/main.do

Use for standard word meanings, headword checks, and conservative wording when correctness matters. Prefer it over casual web usage when writing public, academic, or formal text.

### Urimalsaem

URL: https://opendict.korean.go.kr/main

Use as an open Korean lexicon for newer or broader usage signals. Because it is participatory, verify sensitive or formal wording with the Standard Korean Dictionary or another official source before treating it as final.

### National Korean corpora

URL: https://kli.korean.go.kr/corpus/main/requestMain.do

Use as a pointer to real Korean language data: newspapers, online posts, everyday conversation, and analyzed corpora. Do not claim corpus-backed evidence unless you actually checked corpus examples in the current task.

### AI Malpyeong

URL: https://kli.korean.go.kr/benchmark/home.do

Use as a signal that Korean AI evaluation includes Korean usage, writing, grammar QA, dialogue context, summarization, and inappropriate-speech tasks. Do not overclaim it as a direct source for "AI-writing tells"; use it to frame evaluation dimensions for Korean language quality.

### Korean orthography and foreign-word spelling

URL: https://korean.go.kr/kornorms

Use when spelling, spacing, punctuation, standard-language, or foreign-word transliteration matters. If the live rules page is unavailable in the current environment, say that the rule could not be verified live and avoid making a hard correction unless it is well-established.

## Practical Hierarchy

1. Preserve the user's meaning, facts, and intended reader relationship.
2. Make the sentence understandable before making it elegant.
3. Prefer specific verbs over abstract nouns.
4. Replace foreign words only when the Korean alternative is clearer for the reader.
5. Keep technical terms when the target audience expects them.
6. Surface missing evidence instead of filling gaps with plausible detail.
7. Treat public copy more strictly than casual posts.

## Korean Rewrite Checklist

- Is the register stable?
- Are sentence endings repetitive?
- Does the text rely on `또한`, `이를 통해`, or `전반적으로` instead of real transitions?
- Are claims specific enough to stand without inflated praise?
- Are there vague authorities or unsupported generalizations?
- Can nominalized phrases become verbs?
- Are parentheses, slashes, and English words helping the reader?
- Did the rewrite preserve names, quoted text, legal wording, and technical terms that should not change?
