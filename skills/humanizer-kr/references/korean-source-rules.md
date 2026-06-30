# Korean Source Rules

Use this file when a Korean rewrite needs source-grounded judgment rather than taste alone.

## Trusted Source Map

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
