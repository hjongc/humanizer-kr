# Release Checklist

Use this checklist before publishing Humanizer KR to GitHub, a Codex marketplace, or a Claude plugin marketplace.

## Required

- [ ] Replace every `https://github.com/hjongc/humanizer-kr` placeholder with the final repository URL.
- [ ] Confirm `LICENSE` is present and matches the manifest license.
- [ ] Confirm `.codex-plugin/plugin.json` parses as JSON.
- [ ] Confirm `.claude-plugin/plugin.json` parses as JSON.
- [ ] Confirm `skills/humanizer-kr/SKILL.md` has frontmatter with `name` and `description`.
- [ ] Confirm every script referenced by `SKILL.md` exists.
- [ ] Run `python3 scripts/sync_plugin_package.py`.
- [ ] Run `python3 scripts/validate_package.py --release`.
- [ ] Run the audit script against at least one example file.

## Codex

- [ ] Add this repo as a Codex marketplace in a temporary `CODEX_HOME`.
- [ ] Confirm `codex plugin list --available --json` shows `humanizer-kr`.
- [ ] Install `humanizer-kr@humanizer-kr-marketplace`.
- [ ] Install from the local plugin directory if testing direct plugin install.
- [ ] Restart Codex.
- [ ] Invoke `$humanizer-kr` on `examples/product-copy.before.ko.md`.
- [ ] Confirm the rewritten answer preserves facts and does not add invented claims.

## Claude Code

- [ ] Load the local plugin directory.
- [ ] Add this repo as a Claude marketplace in a temporary `HOME`.
- [ ] Confirm `claude plugin install humanizer-kr@humanizer-kr-marketplace` succeeds.
- [ ] Validate the Claude plugin with the installed Claude tooling.
- [ ] Invoke the skill through the Claude plugin namespace.
- [ ] Confirm the rewritten answer preserves facts and does not add invented claims.

## Public Release

- [ ] Add GitHub topics or README badges only after the repository is live.
- [ ] Tag the release with the version in `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, and the latest `CHANGELOG.md` heading.
- [ ] Keep marketplace entries pointing at an immutable tag or commit SHA for public distribution.
