# Pattern Candidates

Use this file for suspected Korean AI-writing tells that are not ready to become
rules. A candidate should stay here until it has enough evidence, a clear edit
strategy, and regression coverage.

## Promotion Criteria

- Reproduces in at least two different genres or source contexts.
- Has a concrete edit strategy that preserves facts and register.
- Does not flag clean after examples in `examples/*.after.ko.md`.
- Has a regression test for detection and at least one clean negative example.
- Does not turn the skill into an AI detector or authorship classifier.

## Status Labels

- `pending`: observed, but evidence is still thin.
- `promoted`: added to `audit_korean_text.py`, `SKILL.md`, or the playbook.
- `merged`: covered by an existing rule after review.
- `rejected`: too broad, too noisy, or not specific to Korean quality.

## Candidate Template

```text
### CAND-YYYY-NNN: Short name

Status: pending
Observed in: product-copy | notice | support-email | docs | proposal | social-post
Suspected pattern:
Why it may hurt the text:
False-positive risk:
Preferred edit:
Evidence:
- 
Promotion decision:
Regression coverage:
```

## Current Candidates

### CAND-2026-001: Decorative contrast opener

Status: pending
Observed in: product-copy, social-post
Suspected pattern: `단순한 X가 아닙니다`, `그저 X가 아니라 Y입니다`, and similar contrast
openers used before the actual claim.
Why it may hurt the text: the sentence spends attention on a theatrical frame
instead of saying what the product or idea does.
False-positive risk: contrast can be useful in positioning copy when the user
actually needs to correct a misconception.
Preferred edit: keep the contrast only when the audience misconception is
explicit; otherwise start with the concrete behavior or benefit.
Evidence:
- Common in AI-generated product blurbs, but not yet verified across enough
  local examples.
Promotion decision: keep pending until two real before examples and one clean
negative example exist.
Regression coverage: none yet.

### CAND-2026-002: Courtesy stack in support replies

Status: pending
Observed in: support-email, public-notice
Suspected pattern: multiple polite wrappers in one short reply, such as
`불편을 드려 죄송합니다`, `양해 부탁드립니다`, `확인 부탁드립니다`, and
`감사합니다` all appearing around a single action.
Why it may hurt the text: the action becomes harder to find even though each
phrase is individually natural.
False-positive risk: apology and thanks are sometimes required in customer
support.
Preferred edit: keep one relationship signal, then name the next action.
Evidence:
- Adjacent to the existing `honorific-padding` and `weak-reader-action` rules,
  but may need frequency and genre thresholds before promotion.
Promotion decision: keep pending; merge into existing rules if it cannot be
made precise.
Regression coverage: none yet.

