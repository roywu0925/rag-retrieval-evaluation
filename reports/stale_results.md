# Stale-fact results (scripts/analyze_stale.py; rule: reports/stale_fact_rule.md, frozen)

> **AUDIT VERDICT. Read this before any number below.** Every class, rate and test in this file is the frozen RULE's output. The pre-registered blind hand audit (reports/audit/agreement.md) found the rule wrong on 31 of the 36 answers that drive its propagation count. Population agreement is 0.64, below the 0.85 threshold, so these results are RULE-DEPENDENT. The rule's pooled 39% propagation is about 10x the audited estimate of 4% (5/132; two-sided 95% upper bound 17%; reports/audit/propagation_rate.json), and all 5 propagated answers are on the unmarked facts SF10 and SF11. See reports/finding_c_stale_facts.md.

Descriptive by design (rule section 4): n = 11 facts per cell. A mitigation counts as an effect only if exact McNemar rejects. Abstention is measured under an explicit abstention instruction (upper bound).

## Rates per arm x condition (denominator = all answers)

| arm | condition | propagated (11) | propagated (8, excl. SF3/10/11) | current (11) | abstain (11) | S1 propagated | S2 propagated |
|---|---|---|---|---|---|---|---|
| claude-haiku-4-5-2025100 | baseline | 4/11 [15-65%] | 2/8 | 5/11 | 1/11 | 1/11 | 5/11 |
| claude-haiku-4-5-2025100 | exclude_context | 5/11 [21-72%] | 3/8 | 6/11 | 0/11 | 3/11 | 6/11 |
| claude-haiku-4-5-2025100 | recency_git | 5/11 [21-72%] | 2/8 | 5/11 | 1/11 | 4/11 | 5/11 |
| claude-haiku-4-5-2025100 | corrections_doc (repeats of baseline) | 4/11 [15-65%] | 2/8 | 5/11 | 1/11 | 1/11 | 5/11 |
| claude-sonnet-4-6 | baseline | 5/11 [21-72%] | 2/8 | 6/11 | 0/11 | 2/11 | 5/11 |
| claude-sonnet-4-6 | exclude_context | 4/11 [15-65%] | 3/8 | 7/11 | 0/11 | 1/11 | 4/11 |
| claude-sonnet-4-6 | recency_git | 4/11 [15-65%] | 2/8 | 6/11 | 0/11 | 1/11 | 4/11 |
| claude-sonnet-4-6 | corrections_doc (repeats of baseline) | 5/11 [21-72%] | 2/8 | 6/11 | 0/11 | 2/11 | 5/11 |
| claude-opus-4-6-v1 | baseline | 5/11 [21-72%] | 2/8 | 6/11 | 0/11 | 1/11 | 5/11 |
| claude-opus-4-6-v1 | exclude_context | 2/11 [5-48%] | 1/8 | 9/11 | 0/11 | 1/11 | 3/11 |
| claude-opus-4-6-v1 | recency_git | 5/11 [21-72%] | 2/8 | 6/11 | 0/11 | 1/11 | 5/11 |
| claude-opus-4-6-v1 | corrections_doc (repeats of baseline) | 4/11 [15-65%] | 2/8 | 7/11 | 0/11 | 1/11 | 4/11 |

## All seven classes

| arm | condition | CURRENT | CURRENT_FLAGGED | MIXED | PROPAGATED | OLD_FLAGGED | ABSTAIN | OTHER |
|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5-2025100 | baseline | 4 | 1 | 3 | 1 | 0 | 1 | 1 |
| claude-haiku-4-5-2025100 | exclude_context | 5 | 1 | 2 | 3 | 0 | 0 | 0 |
| claude-haiku-4-5-2025100 | recency_git | 4 | 1 | 1 | 4 | 0 | 1 | 0 |
| claude-haiku-4-5-2025100 | corrections_doc | 4 | 1 | 3 | 1 | 0 | 1 | 1 |
| claude-sonnet-4-6 | baseline | 4 | 2 | 3 | 2 | 0 | 0 | 0 |
| claude-sonnet-4-6 | exclude_context | 5 | 2 | 3 | 1 | 0 | 0 | 0 |
| claude-sonnet-4-6 | recency_git | 4 | 2 | 3 | 1 | 0 | 0 | 1 |
| claude-sonnet-4-6 | corrections_doc | 4 | 2 | 3 | 2 | 0 | 0 | 0 |
| claude-opus-4-6-v1 | baseline | 4 | 2 | 4 | 1 | 0 | 0 | 0 |
| claude-opus-4-6-v1 | exclude_context | 5 | 4 | 1 | 1 | 0 | 0 | 0 |
| claude-opus-4-6-v1 | recency_git | 4 | 2 | 4 | 1 | 0 | 0 | 0 |
| claude-opus-4-6-v1 | corrections_doc | 4 | 3 | 3 | 1 | 0 | 0 | 0 |

## Mitigation vs baseline, paired over the 11 facts (exact McNemar; Newcombe CI; Holm within arm)

| arm | mitigation | fixed | broken | stayed prop. | stayed not | drop in propagation [95% CI] | p | p Holm | effect? |
|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5-2025100 | exclude_context | 1 | 2 | 3 | 5 | -9 pts [-35, +19] | 1.000 | 1.000 | no (direction only) |
| claude-haiku-4-5-2025100 | recency_git | 0 | 1 | 4 | 6 | -9 pts [-24, +7] | 1.000 | 1.000 | no (direction only) |
| claude-sonnet-4-6 | exclude_context | 2 | 1 | 3 | 5 | +9 pts [-19, +35] | 1.000 | 1.000 | no (direction only) |
| claude-sonnet-4-6 | recency_git | 1 | 0 | 4 | 6 | +9 pts [-7, +24] | 1.000 | 1.000 | no (direction only) |
| claude-opus-4-6-v1 | exclude_context | 3 | 0 | 2 | 6 | +27 pts [+0, +50] | 0.250 | 0.500 | no (direction only) |
| claude-opus-4-6-v1 | recency_git | 0 | 0 | 5 | 6 | +0 pts [-2, +2] | 1.000 | 1.000 | no (direction only) |

At n = 11 the smallest rejecting outcome is 6 fixed / 0 broken. 'No' means this design could not detect it, not that there is no effect.

## Sensitivity lines: does the mitigation ORDER change?

**FINDING: the ordering changes under a sensitivity line** (rule section 2, reported in the main text):
- us.anthropic.claude-haiku-4-5-20251001-v1:0: S1 gives {'baseline': 1, 'exclude_context': 3, 'recency_git': 4} vs headline {'baseline': 4, 'exclude_context': 5, 'recency_git': 5}
- us.anthropic.claude-haiku-4-5-20251001-v1:0: S2 gives {'baseline': 5, 'exclude_context': 6, 'recency_git': 5} vs headline {'baseline': 4, 'exclude_context': 5, 'recency_git': 5}
- us.anthropic.claude-opus-4-6-v1: S1 gives {'baseline': 1, 'exclude_context': 1, 'recency_git': 1} vs headline {'baseline': 5, 'exclude_context': 2, 'recency_git': 5}

## Noise floor: corrections_doc answers are repeats of baseline (identical prompts)

| arm | prompts identical | answers differ textually | answers change class |
|---|---|---|---|
| claude-haiku-4-5-2025100 | 12/12 | 0/12 | 0/12 |
| claude-sonnet-4-6 | 12/12 | 5/12 | 0/12 |
| claude-opus-4-6-v1 | 12/12 | 7/12 | 1/12 |

The Haiku stability check (two baseline runs before the main run): 0/12 textual, 0/12 class changes.

## Marked (SF1-SF9) vs unmarked (SF10, SF11) facts: propagated count

| arm | condition | marked (of 9) | unmarked (of 2) |
|---|---|---|---|
| claude-haiku-4-5-2025100 | baseline | 2 | 2 |
| claude-haiku-4-5-2025100 | exclude_context | 4 | 1 |
| claude-haiku-4-5-2025100 | recency_git | 3 | 2 |
| claude-sonnet-4-6 | baseline | 3 | 2 |
| claude-sonnet-4-6 | exclude_context | 4 | 0 |
| claude-sonnet-4-6 | recency_git | 2 | 2 |
| claude-opus-4-6-v1 | baseline | 3 | 2 |
| claude-opus-4-6-v1 | exclude_context | 2 | 0 |
| claude-opus-4-6-v1 | recency_git | 3 | 2 |

## Retrieval class x answer bucket (all arms, per condition)

- baseline: both->current: 15, both->propagated: 6, current-only->current: 2, current-only->neither: 1, old-only->neither: 1, old-only->propagated: 8
- exclude_context: both->current: 12, both->propagated: 6, current-only->current: 8, current-only->propagated: 1, neither->current: 2, neither->propagated: 1, old-only->propagated: 3
- recency_git: both->current: 15, both->propagated: 6, current-only->current: 2, current-only->neither: 1, old-only->neither: 1, old-only->propagated: 8

## X1 (hallucination probe)

- claude-haiku-4-5-20251001-v1:0: baseline=CORRECT, exclude_context=CORRECT, recency_git=CORRECT, corrections_doc=CORRECT
- claude-sonnet-4-6: baseline=CORRECT, exclude_context=CORRECT, recency_git=CORRECT, corrections_doc=CORRECT
- claude-opus-4-6-v1: baseline=CORRECT, exclude_context=CORRECT, recency_git=CORRECT, corrections_doc=CORRECT

## Per fact (class per arm, baseline / exclude_context / recency_git)

| fact | retrieval at baseline | claude-haiku-4-5-2 | claude-sonnet-4-6 | claude-opus-4-6-v1 |
|---|---|---|---|---|
| SF1 | both | CURRENT / CURRENT / CURRENT_FLAGGED | CURRENT_FLAGGED / CURRENT / CURRENT_FLAGGED | CURRENT_FLAGGED / CURRENT_FLAGGED / CURRENT_FLAGGED |
| SF2 | both | CURRENT / CURRENT / CURRENT | CURRENT_FLAGGED / CURRENT_FLAGGED / CURRENT_FLAGGED | CURRENT_FLAGGED / CURRENT_FLAGGED / CURRENT_FLAGGED |
| SF3 (retrieval-limited) | old-only | OTHER / PROPAGATED / PROPAGATED | PROPAGATED / PROPAGATED / OTHER | PROPAGATED / PROPAGATED / PROPAGATED |
| SF4 | both | PROPAGATED / PROPAGATED / PROPAGATED | PROPAGATED / MIXED / PROPAGATED | MIXED / CURRENT_FLAGGED / MIXED |
| SF5 | both | CURRENT / PROPAGATED / CURRENT | CURRENT / CURRENT / CURRENT | CURRENT / CURRENT / CURRENT |
| SF6 | current-only | ABSTAIN / CURRENT / ABSTAIN | CURRENT / CURRENT / CURRENT | CURRENT / CURRENT / CURRENT |
| SF7 | both | MIXED / MIXED / MIXED | MIXED / MIXED / MIXED | MIXED / MIXED / MIXED |
| SF8 | both | CURRENT_FLAGGED / CURRENT_FLAGGED / CURRENT | CURRENT / MIXED / CURRENT | CURRENT / CURRENT_FLAGGED / CURRENT |
| SF9 | both | CURRENT / CURRENT / CURRENT | CURRENT / CURRENT_FLAGGED / CURRENT | CURRENT / CURRENT / CURRENT |
| SF10 (retrieval-limited) | old-only | MIXED / MIXED / PROPAGATED | MIXED / CURRENT / MIXED | MIXED / CURRENT / MIXED |
| SF11 (retrieval-limited) | old-only | MIXED / CURRENT / PROPAGATED | MIXED / CURRENT / MIXED | MIXED / CURRENT / MIXED |

## Hand audit (rule section 6)

58 answers for Roy, blind to the rule's class: all 36 MIXED/OLD_FLAGGED/OTHER + 20% (22) of the rest, seed 0. File: eval/stale_audit_blind.jsonl (key held separately). The rule's output stays the headline.
