# Humanizer KR

Humanizer KR is a Korean-specialized writing skill for Codex and Claude Code. It rewrites AI-sounding Korean into natural, context-aware Korean while preserving the user's facts, intent, and register.

It is designed for product copy, public notices, emails, documentation, proposals, posts, and other Korean drafts where stiff translationese, inflated claims, or chatbot-like structure make the writing feel less human.

## What it does

- Rewrites Korean drafts while preserving meaning, facts, paragraph coverage, and register.
- Reviews Korean text for common AI-writing tells such as formulaic praise, stiff translationese, excessive nominalization, repeated passive endings, vague authority claims, and over-structured bullet rhythm.
- Keeps public-facing Korean plain and direct, especially for product copy, announcements, docs, emails, and posts.
- Uses source-grounded vocabulary discipline: do not invent facts, do not force purified words, and check standard or refined terms when wording matters.
- Supports voice calibration from a user-provided Korean writing sample.

## What it is not

Humanizer KR is not an AI detector. The audit script flags patterns that deserve review; it does not prove that a text was written by AI. Do not use this skill to hide plagiarism, impersonate another real person's authorship, or bypass academic, hiring, or compliance integrity checks.

## Repository layout

```text
.codex-plugin/plugin.json          Codex plugin manifest
.claude-plugin/plugin.json         Claude Code plugin manifest
.claude-plugin/marketplace.json    Claude Code marketplace metadata
.agents/plugins/marketplace.json Codex repo marketplace metadata
plugins/humanizer-kr/              Codex marketplace-installable plugin package
skills/humanizer-kr/SKILL.md       Shared skill instructions
skills/humanizer-kr/references/    Korean source-grounding notes
skills/humanizer-kr/scripts/       Local audit helper
examples/                          Before/after Korean examples
scripts/sync_plugin_package.py    Sync marketplace plugin package copy
scripts/validate_package.py        Release smoke validator
```

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
claude plugin marketplace add hjongc/humanizer-kr
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

For an immutable install, pin the release tag when your Claude Code version supports refs in marketplace sources, or clone this repository at `v0.1.1` and add the local path:

```bash
git clone --branch v0.1.1 https://github.com/hjongc/humanizer-kr.git
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

### Review

```text
Use $humanizer-kr to review this Korean copy for AI-like phrasing:
[paste text]
```

### Voice matching

```text
Use $humanizer-kr. Match this sample voice:
[your Korean writing sample]

Rewrite this:
[draft]
```

## Optional local audit

The bundled audit script flags Korean AI-writing tells without rewriting the text:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py path/to/draft.md
```

or:

```bash
printf '또한 본 솔루션은 혁신적인 경험을 제공합니다.' | python3 skills/humanizer-kr/scripts/audit_korean_text.py
```

Machine-readable output is available with:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py --json path/to/draft.md
```

## Validate before release

After editing the root skill or manifests, sync the marketplace package copy:

```bash
python3 scripts/sync_plugin_package.py
```

Then run the package validator from the repository root. It checks both the root authoring copy and the marketplace package copy:

```bash
python3 scripts/validate_package.py
```

Then run a content smoke test:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py examples/product-copy.before.ko.md
```

See `RELEASE_CHECKLIST.md` for the full publishing checklist.

## Examples

- `examples/product-copy.before.ko.md` -> `examples/product-copy.after.ko.md`
- `examples/public-notice.before.ko.md` -> `examples/public-notice.after.ko.md`

The example outputs are reference rewrites, not the only acceptable answers.

## Source basis

See `skills/humanizer-kr/references/korean-source-rules.md` for the trusted Korean source map and how the skill uses each source.

## Limitations

- The skill improves wording and register; it does not verify factual claims unless the user provides sources.
- The audit script is conservative and pattern-based. Clean output does not guarantee polished Korean.
- Claude Code plugin behavior can vary by installed Claude Code version. Validate locally before publishing to a Claude marketplace.

## License

MIT
