# Output-Feedback Improvement Loop

Maintainer-only. Not synced into `plugins/humanizer-kr` (see `scripts/sync_plugin_package.py`).

The release gate (`--after-examples`) only proves that hand-written examples pass
hand-written regexes. This loop measures what the skill actually produces and
feeds failures back into `SKILL.md`, the playbook, and the audit rules.

## Layout

```
evals/
  inputs/<id>.ko.md        AI-flavored drafts to rewrite (frontmatter below)
  human/<id>.ko.md         human-written Korean; audit false-positive set
  loop.py                  run | judge | pick | report
  rounds/<n>/              one directory per round (committed)
    meta.json              skill git SHA, models, date
    outputs/<engine>/<condition>/<id>.md
    judge.jsonl            one LLM verdict per output
    picks.jsonl            human blind picks
    report.md              round summary and diff vs previous round
```

Input frontmatter:

```yaml
---
genre: product-copy | public-notice | support-email | proposal | docs | social-post
source: generated | real
must_keep: ["3월 15일", "설정 > 알림", "환불은 7일 이내"]   # facts that must survive
---
```

Set size: 6 genres x 5 = 30 inputs (mix of generated and real), plus the human set.

## Round

1. `run`: rewrite every input with each engine (`codex exec`, `claude -p`) under
   two conditions:
   - `skill`: SKILL.md and both references are put in the prompt, so every engine
     gets the same instructions.
   - `plain`: "Rewrite this Korean text so it reads naturally" with no skill. This
     is the baseline, and it is generated only in round 1 and reused afterwards.
2. `judge`: a fixed judge model scores each output and sees neither the engine
   nor the condition. It returns JSON:
   `{invented: [..], dropped_facts: [..], register_ok, reader_action_ok, genre_fit 1-5, naturalness 1-5, residual_tells: [..], note, rule_violations: [{rule: "S7 or N8", quote: "exact output text"}]}`. The judge uses both sourced rule sets (S and N) at their genre-specific strength.
   `dropped_facts` covers verifiable content only; removed praise, filler, greetings, closing courtesies, and vague expectations do not count. `invented` includes claims strengthened beyond the source, such as an estimate turned into a promise.
   Deterministic checks run alongside it:
   - each `must_keep` string and each number in the source must appear in the
     output, ignoring thousands separators;
   - the audit finding count before and after the rewrite.
3. `pick` (optional): the maintainer is shown 8-10 sampled pairs in random A/B order and
   answers "A, B, or tie". Round 1 pairs `skill` against `plain`; later rounds
   pair the current round against the previous one. When a pick disagrees with
   the judge, the pick wins and the case is logged as a judge miss.
4. `report`: writes `report.md` with these numbers:
   - sourced-rule violation rate and hard-fail rate (any invented content or dropped fact);
   - mean naturalness and genre fit per engine and genre;
   - human win rate;
   - audit false-positive rate on `human/`;
   - the delta against the previous round.

## Triage -> change -> re-run

Classify each failure into one bucket:

- missing rule
- over-editing (content was invented)
- audit false positive
- audit miss
- register or genre mismatch
- judge miss

Fix the smallest owning file: `SKILL.md`, `references/rewriting-playbook.md`, or
the audit rules. Every fix adds a regression case to
`tests/test_audit_korean_text.py` or to `inputs/`.

Re-run on the same set. The sourced-rule violation rate is the primary quality
number alongside the hard-fail rate. Keep a change when the hard-fail rate does
not rise and the sourced-rule violation rate falls; naturalness is secondary.
Otherwise revert it.

## Guardrails

- Never put real personal data into `inputs/` or `human/`. Use only text the
  maintainer owns or may reuse.
- The judge and the pick measure readability. Neither one claims to measure
  "AI detection".
