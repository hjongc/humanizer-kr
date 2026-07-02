# Changelog

All notable changes to Humanizer KR are documented here.

## 0.1.9 - 2026-07-02

- Added `--fail-on-findings` to make the Korean audit helper usable as a local quality gate.
- Added `--after-examples` to audit every public after example with its genre-specific quality pass.
- Updated package validation so public after examples must pass the basic and quality audit before release.
- Removed the speculative pattern-candidates reference from the packaged release surface.

## 0.1.8 - 2026-07-02

- Added a README overview image and a stronger before/after opening.
- Simplified the public README by removing maintainer-only audit, repository layout, and release validation sections.
- Expanded Korean after examples into multiple rewrite candidates.
- Added a sample output-improvement loop fixture.
- Added a naturalness rubric and failure policy to the skill instructions.
- Added `--quality` review mode to the Korean audit helper.

## 0.1.7 - 2026-07-01

- Reorganized the Korean README pattern section into 5 core groups with grouped before/after pattern tables.
- Updated immutable install references to `v0.1.7`.

## 0.1.6 - 2026-07-01

- Updated release documentation to use the stricter package validator.
- Corrected the release checklist so release tags follow the manifest and changelog version.

## 0.1.5 - 2026-07-01

- Reorganized the skill guidance around 5 editing groups while keeping 20 Korean observation patterns.
- Clarified that the 20 patterns are clustered review signals, not a flat banned-word checklist.
- Updated Korean and English README docs to show the 5-group structure and pattern mapping.

## 0.1.4 - 2026-06-30

- Rebuilt the Korean README around the `blader/humanizer` public skill documentation flow.
- Expanded Korean AI-writing coverage to 20 documented patterns.
- Added support email, proposal, product docs, and social post before/after examples.
- Broadened the audit helper and regression tests for Korean-specific tells such as honorific padding, heading warm-ups, synonym cycling, and slogan rhythm.

## 0.1.3 - 2026-06-30

- Made Korean the default README and moved English documentation to `README.en.md`.

## 0.1.2 - 2026-06-30

- Added Korean README documentation.
- Updated GitHub repository About metadata for Korean users.
- Corrected Claude install documentation to prefer HTTPS marketplace URLs.

## 0.1.1 - 2026-06-30

- Added Claude Code marketplace metadata for `claude plugin marketplace add`.
- Documented Claude Code marketplace installation commands.
- Hardened package sync so Claude marketplace metadata does not leak into the installable plugin package.

## 0.1.0 - 2026-06-30

- Added Codex plugin packaging with `skills/humanizer-kr`.
- Added Claude plugin packaging metadata for the same skill source.
- Added Korean writing guidance, source-grounding rules, examples, and smoke tests.
- Added an audit script for flagging Korean AI-writing tells.
