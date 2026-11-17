# Output-Feedback Evaluation Loop

Maintainer-only. Not synced into `plugins/humanizer-kr` (see
`scripts/sync_plugin_package.py`). The evaluation goal is human-likeness: remove
AI-writing tells and translationese while preserving the source's meaning. This
is not a general writing-quality score. A plain, slightly rough human sentence
can be a better result than a polished rewrite that adds structure or claims.

## Layout

```
evals/
  inputs/<id>.ko.md        Korean drafts to rewrite
  human/<id>.ko.md         legacy audit false-positive set
  loop.py                  run | judge | pair | stats | pick | report
  rounds/<n>/              one directory per round
    outputs/<engine>/<condition>/<id>.md
    judge.jsonl            one factual and human-likeness verdict per output
    pair.jsonl             pairwise model judgments
    stats.json             aggregate objective statistics only
    picks.jsonl             optional blind human choices
    report.md               round summary
```

Input frontmatter:

```yaml
---
genre: product-copy | public-notice | support-email | proposal | docs | social-post
source: generated | real
must_keep: ["3월 15일", "설정 > 알림"]
---
```

## Commands

Run the same inputs with the skill or a plain rewrite prompt:

```bash
python3 evals/loop.py run --round 4 --engines codex,claude
python3 evals/loop.py run --round 4 --engines codex --samples 3
python3 evals/loop.py judge --round 4 --judge-engine claude
python3 evals/loop.py pair --round 4 --judge-engine claude
python3 evals/loop.py pair --round 4 --judge-engine claude --all-samples
python3 evals/loop.py stats --round 4 --human ~/.humanizer-kr/samples
python3 evals/loop.py report --round 4 --human ~/.humanizer-kr/samples
```

`run` generates both `skill` and `plain` conditions by default. The plain
baseline is normally created in round 1 and reused in later rounds; pass
`run --round N --with-plain` to generate a fresh one. Each round's `meta.json`
records the skill revision, content digest, dirty flag, models, and date.
Generator calls run in isolated temporary working directories. `--samples K`
generates K resumable outputs for each selected input, engine, and condition
(default 1). Sample 1 keeps `<input-stem>.md`; samples 2 and up use
`<input-stem>~<sample>.md`. Only the conditions selected for that run receive
the requested samples, so an existing single-sample plain baseline can remain
unchanged.

`pick` is an optional blind human comparison. In round 1 it samples skill vs
plain; in later rounds it uses same-round plain when available, otherwise the
previous round's skill output. The judge and pair commands provide separate
model-based measurements.

`pair` compares sample 1 by default. `--all-samples` compares every skill
sample with plain sample 1 when it exists, and with SOURCE. It asks the same judge engine/model twice with A/B
swapped. A win or loss requires agreement across both orders; disagreement is
a tie. Outputs that fail the round's factual hard-fail checks forfeit without a
model call. Each comparison costs two model calls. `--judge-engine fake`
produces deterministic ties for offline tests. Pair records are resumable by
input, engine, comparison, and sample.

The judge returns these required fields:

```json
{
  "invented": [],
  "dropped_facts": [],
  "register_ok": true,
  "ai_tells": [{"tell": "short label", "quote": "exact text from OUTPUT"}],
  "human_likeness": 1,
  "note": "",
  "rule_violations": [{"rule": "S7 or N8", "quote": "exact text", "introduced": true}]
}
```

`human_likeness` measures whether a Korean reader would believe a person wrote
the output, based on the absence of AI-writing tells and translationese. It
does not reward extra structure, completeness, persuasion, or usefulness.
`ai_tells` records each remaining tell with an exact output quote. `invented`
includes asserted additions and modality or tense drift. New reader actions,
headings, lists, examples, and emphasis that assert no new content are noted,
not counted as invented. `dropped_facts` covers lost verifiable information.
Sourced `rule_violations` remain secondary and each entry records whether the
output introduced the issue. Rounds 1–3 used the old schema
(`reader_action_ok`, `genre_fit`, `naturalness`, `residual_tells`); `report`
continues to read those rounds and only calculates metrics present in a row.

`stats` calculates sentence-length mean and coefficient of variation, ending
diversity, connector rate, and a regex-based nominalization proxy for sources,
outputs, and human references. The human directory defaults to
`~/.humanizer-kr/samples` when present. Use `--human DIR` to select another
directory. Human files stay outside the repository: the loop reads `*.md`
files and writes only their count and aggregate metric means to `stats.json` and
the report. It never copies sample text into round artifacts.

## Report order

Reports show factual hard-fail rate first, then human-likeness and AI-tell
summaries, pairwise outcomes, objective-stat distances from the human mean,
and secondary sourced-rule, audit, and optional human-pick results. If no human
reference directory exists, the report says `human reference: none` and prints
no human-distance values. Objective stats can be read from `stats.json` or
computed when reporting. Round deltas compare common skill inputs against the
previous round and include factual hard-fail rate and human-likeness. A
naturalness delta is included only when both rounds contain that legacy metric.
Hard-fail output rates include a 95% Wilson score interval. When a group has
multiple samples per input, the report also shows how many inputs failed in at
least one sample and in every sample. Round deltas compare hard-fail rates over
the common inputs and show the sample count used for each round.
The report also includes the legacy audit false-positive rate over `evals/human/`.

## Triage

Use factual hard failures, AI-tell labels, pairwise results, and the secondary
sourced-rule section to find over-editing, remaining AI tells, audit misses, or
judge disagreements. Change the smallest owning skill, reference, or audit
rule, add a regression case, and rerun the same evaluation set.

## Guardrails

- Never put real personal data into committed `inputs/` or the legacy `human/`
  set. Human reference samples should remain outside the repository.
- The judge and pairwise comparison measure human-likeness, not authorship or
  AI detection.
- Deterministic fact checks verify `must_keep` strings and source numbers.
