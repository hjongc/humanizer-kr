# Changelog

All notable changes to Humanizer KR are documented here.

## 0.3.1 - 2026-11-18

- Added `/humanizer-kr:feedback` and the equivalent Codex task for explicit voice preferences, correction pairs/reasons, and comparison feedback.
- Only an explicit preference changes the profile; example edits and A/B choices remain records without inferred rules.
- Added private profile backups and undo, guarded by hashes and a local writer lock so newer edits are not silently overwritten.
- Preserved existing voice lookup, profile formats, samples, and ordinary writing behavior.

## 0.3.0 - 2026-11-17

- Added Claude Code slash commands for style analysis, voice rewriting, and new composition.
- Analysis now saves samples and an evidence-based `voice.md` by default; later writing automatically applies it.
- Update the active profile directory by default so new analysis is not hidden behind an older project profile; preserve explicit manual preferences on rebuild.
- Separated minimal AI-tell cleanup from voice rewriting and new composition, keeping factual constraints.
- Added held-out voice-fidelity comparisons and blind user preferences, separate from generic human-likeness.
- Made the multi-sample report test independent of concurrent result order.

## 0.2.0 - 2026-11-17

- Re-aimed rewrite guidance at removing AI-writing tells and translationese while preserving source meaning, facts, and level of detail.
- Added personal voice profiles: pasted samples are saved under `~/.humanizer-kr/samples/` (or a project `.humanizer-kr/`) and summarized into `voice.md`.
- Added official-source sentence rules (MOLEG S1-S13, NIKL N1-N13) with a small default set and opt-in public-language rules.
- Added a Meaning Lock: modality, hedges, hearsay, tense, qualifiers, restrictors, conditions, causal connectives, and proper nouns stay as in the source.
- Limited edits to spans that carry an AI tell; sentences without a tell are copied unchanged.
- Added `--source` to the audit script to flag numbers, UI paths, quotes, and modality dropped from the original.
- Added a maintainer-only output-feedback eval loop (`evals/`).

## 0.1.10 - 2026-07-02

- Removed README overview images from the public Korean and English docs.
- Simplified the opening example so it ends at the Before/After rewrite.
- Updated install snippets to point at the `v0.1.10` release tag.

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
