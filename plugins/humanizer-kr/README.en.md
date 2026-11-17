# Humanizer KR

English | [한국어](README.md)

Humanizer KR is a Korean writing skill for Codex and Claude Code that removes AI-writing tells and translationese so text reads as written by a person, while preserving its meaning, facts, and the writer's level of detail.

It is designed for product copy, public notices, emails, documentation, proposals, posts, and other Korean drafts where stiff translationese, inflated claims, or chatbot-like structure make the writing feel less human.

## Example

Humanizer KR does not make Korean copy louder. It removes the padding, inflated claims, and translated-outline rhythm so the reader can understand the point faster. In business contexts, it keeps useful business language instead of flattening everything into plain everyday Korean.

**Before**

> 충분한 물을 마시는 것은 건강한 생활 습관 형성에 도움을 줄 수 있습니다. 또한 이를 통해 몸의 수분 균형을 유지하고 일상생활에서 더 나은 컨디션을 기대할 수 있습니다.

**After**

> 물을 충분히 마시면 몸의 수분 균형을 유지하는 데 도움이 됩니다. 일상에서 컨디션을 관리하기에도 좋습니다.

## When to use it

- Everyday writing or explanatory text feels stiff because of translationese or abstract wording.
- Product copy feels flat, overexplained, or too promotional.
- Notices, emails, and docs are weighed down by ceremonial honorifics.
- Proposals or reports make claims that are larger than the evidence.
- Social posts sound like slogan fragments or chatbot politeness.
- You want Korean output to match a provided writing sample instead of generic polished Korean.

## 5 editing groups, 20 observation patterns

Humanizer KR does not treat the 20 patterns as a flat banned-word list. The skill rewrites through five editing groups, then uses the 20 patterns as Korean-specific observation signals inside those groups.

1. Evidence and claim strength
2. Translationese and vocabulary density
3. Actors and verbs
4. Register and relationship
5. Structure and rhythm

The 20 documented patterns are:

| Group | Patterns |
| --- | --- |
| Evidence and claim strength | inflated praise, vague authority, knowledge-gap disclaimers, generic positive conclusions, stacked hedging |
| Translationese and vocabulary density | translation-like connectors, English-first word choice, synonym cycling |
| Actors and verbs | nominalized Korean, passive or availability chains |
| Register and relationship | register drift, chatbot artifacts, honorific padding, sycophantic or fake-candid openers |
| Structure and rhythm | over-structured chatbot formatting, punctuation and parenthesis clutter, heading warm-ups, bold-label lists, change-anchored documentation, uniform cadence and slogan rhythm |

## What it does

- Rewrites Korean drafts while preserving meaning, facts, paragraph coverage, and register.
- Reviews Korean text for common AI-writing tells such as formulaic praise, stiff translationese, excessive nominalization, repeated passive endings, vague authority claims, and over-structured bullet rhythm.
- Keeps public-facing Korean plain and direct, especially for product copy, announcements, docs, emails, and posts.
- Uses source-grounded vocabulary discipline: do not invent facts, do not force purified words, and check standard or refined terms when wording matters.
- Supports voice calibration from a user-provided Korean writing sample.

## What it is not

Humanizer KR is not an AI detector. The audit script flags patterns that deserve review; it does not prove that a text was written by AI. Do not use this skill to hide plagiarism, impersonate another real person's authorship, or bypass academic, hiring, or compliance integrity checks.

## Install in Codex

### Local plugin install

Use this repository folder as the plugin root. The Codex manifest is:

```text
.codex-plugin/plugin.json
```

After installing or copying the plugin, restart Codex so it reloads the skill metadata. Invoke the skill explicitly with:

```text
Use $humanizer-kr to make this Korean draft sound natural:
[paste text]
```

### Direct skill install

For a personal local install without plugin metadata, copy the skill folder into a Codex skills directory:

```text
skills/humanizer-kr/ -> ~/.codex/skills/humanizer-kr/
```

Restart Codex and invoke `$humanizer-kr`.

### Marketplace publishing

This repository includes `.agents/plugins/marketplace.json` so it can act as a Codex repo marketplace. The marketplace entry points at `plugins/humanizer-kr`, which is the installable plugin package Codex expects. Before publishing, replace every `https://github.com/hjongc/humanizer-kr` placeholder in the manifests and docs with the final repository URL. For public distribution, prefer an immutable tag or commit SHA.

## Install in Claude Code

This repository also includes a Claude Code plugin manifest:

```text
.claude-plugin/plugin.json
```

Add the repository as a Claude Code marketplace, then install the plugin:

```bash
claude plugin marketplace add https://github.com/hjongc/humanizer-kr.git
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

For an immutable install, clone this repository at `v0.3.0` and add the local path:

```bash
git clone --branch v0.3.0 https://github.com/hjongc/humanizer-kr.git
claude plugin marketplace add ./humanizer-kr
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

Depending on the Claude Code version and install path, the skill may be invoked under the plugin namespace, for example:

```text
/humanizer-kr:humanizer-kr
```

Validate the plugin before publishing or debugging local changes:

```bash
claude plugin validate plugins/humanizer-kr
```

## Use

### Rewrite

```text
Use $humanizer-kr to make this Korean draft sound natural:
[paste text]
```

### Rewrite with one quality loop

```text
Use $humanizer-kr. Rewrite this, then review the result once and improve it again:
[paste text]
```

### Review

```text
Use $humanizer-kr to review this Korean copy for AI-like phrasing:
[paste text]
```

### File audit gate

Use the audit helper to review AI-writing tells in Korean files. The basic audit and `--quality` results are review signals, not grounds for adding actions or specificity that the source does not contain.

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py --quality --genre product-copy --fail-on-findings examples/product-copy.after.ko.md
```

To check every public after example with its genre-specific quality pass, run:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py --after-examples
```

### Style analysis and personalized writing

Claude Code provides task-specific slash commands. Install `v0.3.0` or later and restart Claude Code.

```text
/humanizer-kr:analyze [your writing or file path]
/humanizer-kr:rewrite [draft and voice sample, or use the saved profile]
/humanizer-kr:write [topic, reader, purpose, and supplied facts]
```

Analyze reports observed endings, sentence rhythm, paragraph progression, vocabulary, and emotional color with evidence. It saves the raw samples and creates or rebuilds `voice.md` by default, without rewriting the input or asking for a second confirmation. To opt out, use `/humanizer-kr:analyze Analyze without saving: [my writing]`.

Voice rewrite can change endings, rhythm, and paragraph construction throughout while preserving claims. Voice write creates new text from a brief; samples supply voice, never new facts or personal experiences. Both ask for a sample when no sample/profile exists. Ordinary AI-tell removal still uses minimal edits.

In Codex, select the same tasks through `$humanizer-kr`:

```text
Use $humanizer-kr. Analyze my Korean writing style: [my writing]
Use $humanizer-kr. Rewrite this in my voice: [draft and sample]
Use $humanizer-kr. Write in my saved voice. Topic: [...]. Reader: [...]. Purpose: [...]. Facts: [...].
```

Analysis saves samples and a derived `voice.md` unless explicitly opted out. An explicit storage selection wins; otherwise update the active profile directory (project first, then personal). With no existing profile, start in `~/.humanizer-kr/`. Store raw writing in the selected directory's `samples/`. If personal storage is explicitly selected while a project profile exists, that project profile still takes precedence when writing in this project. Each observed feature records its sample ID, a short privacy-safe quote, genre scope, and evidence sufficiency. A one-off phrase is not an always-use preference, and a work-email sample does not establish a chat style.

Later rewrites and new compositions through this skill automatically load and apply `voice.md`; the user does not need to select their voice again. Current instructions can override or disable it. Raw samples are not reloaded. Adding samples rebuilds it from all saved samples. Profiles remain hand-editable; existing profiles still work. Consider ignoring `.humanizer-kr/` for project storage. Before returning output, check voice alignment, factual preservation, and sample copying separately. This workflow is not proof of voice fidelity; see [evaluation guidance](https://github.com/hjongc/humanizer-kr/blob/main/evals/README.md).

## Examples

- `examples/product-copy.before.ko.md` -> `examples/product-copy.after.ko.md`
- `examples/public-notice.before.ko.md` -> `examples/public-notice.after.ko.md`
- `examples/support-email.before.ko.md` -> `examples/support-email.after.ko.md`
- `examples/proposal.before.ko.md` -> `examples/proposal.after.ko.md`
- `examples/docs.before.ko.md` -> `examples/docs.after.ko.md`
- `examples/social-post.before.ko.md` -> `examples/social-post.after.ko.md`

The after examples include multiple rewrite candidates such as a safe version, a warmer version, and a shorter version. They are reference rewrites, not the only acceptable answers.

## Source basis

- The Korean Ministry of Government Legislation's *Easy-to-Understand Statutes Drafting Standards*, 10th edition (revised and expanded), is the source for sentence rules S1–S13.
- The Ministry of Culture, Sports and Tourism and National Institute of Korean Language's *Guide to Writing Easy Public Language* (2014), and NIKL's *Public Language Made Easy at a Glance*, revised edition (2022), are the sources for public-language rules N1–N13.

See `skills/humanizer-kr/references/korean-source-rules.md` for the trusted Korean source map and how the skill uses each source.

Use `skills/humanizer-kr/references/rewriting-playbook.md` for pattern-specific rewrite strategies and over-editing guardrails.

## Limitations

- It is built for AI-written drafts. On text a person already wrote, it can still reword sentences and shift their meaning slightly, so do not run it on human-written text.
- The skill improves wording and register; it does not verify factual claims unless the user provides sources.
- The audit script is conservative and pattern-based. Clean output does not guarantee polished Korean.
- Claude Code plugin behavior can vary by installed Claude Code version. Validate locally before publishing to a Claude marketplace.

## License

MIT
