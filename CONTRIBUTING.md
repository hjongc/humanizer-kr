# Contributing

Humanizer KR is a writing-quality skill, so changes should improve Korean output while preserving facts and user intent.

## Principles

- Keep the skill source-grounded. Do not add made-up grammar rules, style authorities, or unverifiable claims.
- Preserve user meaning. Rewrites may change wording and rhythm, not facts.
- Avoid AI-detection claims. The audit script flags patterns that deserve review; it does not prove text was written by AI.
- Keep examples realistic and modest. Public-facing examples should not imply unsupported product claims.

## Release Checks

Before publishing a release:

1. Run `python3 scripts/validate_package.py`.
2. Run `python3 skills/humanizer-kr/scripts/audit_korean_text.py examples/product-copy.before.ko.md`.
3. Install the plugin locally in Codex and confirm `$humanizer-kr` appears after restart.
4. Install or load the plugin locally in Claude Code and confirm the skill appears under the plugin namespace.
5. Replace placeholder repository URLs in manifests and docs.
