# Finding (c): do retrieval and answers repeat superseded values?

Sources: logs/stale_answers.jsonl (144 answers), the pre-registered rule reports/stale_fact_rule.md (frozen
2026-11-06T22:57:26Z), and the hand audit reports/audit/agreement.md (58 answers, labelled blind by Roy).

## Headline, with the audit's verdict attached

The pre-registered rule classifies **52 of 132 fact answers (39%) as propagated**. That is 11 stale facts × 4
conditions × 3 model arms (Haiku 4.5, Sonnet 4.6, Opus 4.6). It is the headline because the pre-registration names
the rule's output as the headline. **The pre-registered hand audit shows this number is wrong by about a factor of
ten.** On the auditor's labels, about **5 of 132 answers (4%; 95% upper bound 17%)** would leave a reader believing a
superseded value is current. On the 36 answers that produce most of the rule's 39% (every answer the rule classed
MIXED or OTHER, audited in full), the rule and the auditor agreed on **5 of 36 (0.14)**. Population-weighted
agreement over all 132 answers is 0.64, below the pre-registered 0.85 threshold, so every rule-based stale-fact
number is labelled rule-dependent. The 39% must not be quoted without this paragraph.

The substantive finding below therefore rests on the human labels. The rule was built as a conservative,
deterministic **proxy** for one question: would a reader of this answer be misled? The audit measured the proxy
against that question directly, and the proxy failed. The pre-registration kept the rule as the headline. It
never claimed the rule was right, and it pre-registered the audit (rule section 6) as the measurement of the rule's
error. That measurement is what this section reports.

How the 4% is estimated:
- All 36 rule-fragile answers were labelled, and 5 of them are propagated.
- 18 of the other 96 fact answers were sampled at random (seed 0) and labelled, and none is propagated.
- The lower bound, 5/132 = 3.8%, is exact.
- The upper bound, 17%, takes the Clopper-Pearson 95% upper limit of 0/18 (0.185) for the unsampled stratum:
  (5 + 0.185 × 96) / 132.

## The finding

**All 5 answers the auditor labels propagated are on SF10 and SF11.** These are the only two of the 11 facts that
the corpus does not mark as corrected: status cells in an undated table ("not started") with no correction note.
The 5 answers come from all three model arms (Haiku 2, Sonnet 2, Opus 1).

On the 9 marked facts (SF1-SF9), the auditor labels **none** of the audited answers propagated, in any arm or
condition. That covers 35 audited marked-fact answers: 20 from the fragile census plus 15 from the random sample.

**The cleanest evidence is within a fact.** On SF10 and SF11, the same question to the same model gives a
different answer depending only on which lines retrieval returns. Under `exclude_context`, retrieval for both
facts changes from old-lines-only to current-lines-only:
- **By the rule**, 5 of the 6 (fact, arm) pairs go from MIXED (propagated) to CURRENT. The exception is Haiku on
  SF10, which stays MIXED.
- **By the auditor**, 4 pairs are labelled on both sides:
  - 2 flip to current: Opus SF10 (neither -> current) and Haiku SF11 (propagated -> current).
  - Opus SF11 is current on both sides.
  - Haiku SF10 is "neither" on both sides.
- **Across conditions**, with old-only retrieval the auditor labelled 5 of 15 answers propagated, 7 neither and 3
  current. With current-only retrieval: 3 current and 1 neither, of 4.

These counts are small, but the contrast holds the fact and the model fixed and varies only the context. What it
supports is: **the context decides, not the model.** That is also the pattern across facts. All three arms behave
alike, with near-zero propagation where the context carries a marked correction, and propagation only where it
carries an unmarked old value and no correction.

**What would separate the marker from retrieval, and is missing.** On SF10 and SF11 the correction is unmarked AND
not retrieved, in every condition where the old lines are retrieved. Neither fact ever retrieves old and current
lines together. `exclude_context` also changes both at once: it removes the unmarked old lines and brings in the
current ones. Separating "the correction is not marked" from "the correction is not in the context" needs **an
unmarked fact whose correction IS retrieved alongside the old value. This corpus contains none.** Until that
condition is measured, the claim stops at "the context decides".

**What the audit does not cover.** The rule classed 19 answers PROPAGATED, and 16 of those were not in the audit
sample:
- SF4: 7 (mostly Haiku). The old table values are given without a week-1 scope; the auditor may agree with the rule
  here.
- SF3: 6. Very likely the pattern gap described below.
- SF5: 1. Haiku under `exclude_context`, where removing CONTEXT.md removed the correction itself.
- SF10 and SF11: 1 each.

They enter the 4% only through the random stratum. The 17% upper bound is what allows for them.

**The mitigation comparisons are rule-based** (reports/stale_results.md). They are therefore rule-dependent too.
The audit covers too few answers per cell to redo them on human labels.

## Diagnosis: why the rule failed

The disagreement traces to three specific choices, all made before any answer existed.

1. **The supersession marker must be in the same sentence as the old value** (rule revision 1,
   2026-11-06). Answers that scope the old value in the next sentence were counted as propagated. Example (SF4,
   Opus): "…2.707 yards for Defensive Coverage and 1.174 yards for Targeted Receiver. These figures are from week 1
   only…" The rule says MIXED; the auditor says current (4 of 4 such SF4 answers).
2. **"week 1", "week-1" and "old" were removed from the supersession markers** (rule revision 2, 2026-11-06).
   The reason was real. For SF3, SF6 and SF7, "week 1" is how the old value
   is described, so an answer giving "0.029 on week 1 data" as the answer would otherwise have been counted as
   flagged (OLD_FLAGGED), the flattering class. The cost fell on the other side. Every SF7 answer in every arm and
   condition reads like "3.5% on the full data, while on the week 1 sample it was 4.6%". The rule classed all 12
   MIXED (propagated), and the auditor labelled all 12 current. **This accounts for 12 of the 31 disagreements, all on
   SF7.**
3. **The numeric patterns did not anticipate rounding**, and one fact's site list was incomplete. SF3's `current`
   patterns accept only 0.31 and 1.51. The answers say "about 0.3 yd at 1.9 s" and "past 1.5 yd by 3 s", so answers
   carrying both values were classed PROPAGATED or OTHER. The auditor labelled all 6 audited ones current. The same
   answers show that SF3's current value IS retrieved, through a sentence missing from SF3's `current_sites`. The
   pre-run label "retrieval-limited" for SF3, and its exclusion from the 8-fact rate, were therefore wrong.

The remaining fragile disagreements are SF10 and SF11 MIXED answers that the auditor labels "neither" (8) or
"current" (3). These are hedged status answers ("not done… only partly measured"), where the two simply judge
differently.

The pre-registered sensitivity line S1 (MIXED counted as "neither") pointed in this direction. Under S1, Opus's
`exclude_context` advantage disappeared. The audit shows how far: MIXED was mostly not propagation at all.

The patterns are **not retuned**. The audit stands as the measurement of the rule's error, as pre-registered.

## Agreement statistics, and why kappa is not used

| Stratum | n | Raw agreement | Rule's buckets | Roy's buckets |
|---|---|---|---|---|
| Worksheet 1: census of rule MIXED/OTHER | 36 | 5/36 = 0.14 | 33 propagated, 3 neither | 5 propagated, 23 current, 8 neither |
| Worksheet 2: random sample of the rest | 18 | 15/18 = 0.83 | 15 current, 3 propagated | 18 current |
| Population estimate (strata weighted 36/96) | 132 | 0.64 | | |
| X1 hallucination probe (separate outcomes) | 4 | 4/4 | | |

Confusion matrices (rule class × auditor bucket) are in reports/audit/agreement.md.

**Cohen's kappa is degenerate on both worksheets and is not used as evidence.**
- Worksheet 2: 18 of 18 auditor labels and 15 of 18 rule labels are "current". With almost all mass in one class,
  chance agreement is near the observed agreement, and kappa is 0.00 even though 15 of 18 agree.
- Worksheet 1: the stratum was selected by the rule's own class, so 33 of 36 rule labels are "propagated". Kappa
  (−0.01) is degenerate for the same reason.

The informative statistics are the raw agreement and the confusion matrix. The informative reading of worksheet 1
is not "the rule performed at chance". It is that **the rule was wrong on 31 of the 36 answers that drive its
headline.**

## Methodological finding

We avoided an LLM judge in favour of a deterministic, pre-registered string classifier, on the grounds that it is
objective. On the cases that mattered, it disagreed with a human auditor on 31 of 36. **Determinism is not
accuracy, and an eval classifier needs its own validation.** Here the validation was itself pre-registered: a blind
human audit with a fixed sample, a fixed threshold, and a rule that the classifier's output stays the headline.
That is the only reason the 10× error was caught and not published. Every failure traced to a specific,
documented design choice, made before any answer existed, and each of those choices had a stated rationale. The
reasoning was sound for every choice, and the classifier still failed.
