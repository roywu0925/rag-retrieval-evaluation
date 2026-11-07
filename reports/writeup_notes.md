# Caveats the write-up must carry (recorded before any retrieval was run)

## Eval set
- **Language confound (Tier A vs Tier B).** Tier B questions are Roy's, verbatim in Chinese, and are deliberately
  not translated. The corpus and Tier A are English. Any Tier A / Tier B gap therefore mixes two effects:
  generated vs human-written, and same-language vs cross-lingual retrieval with Titan v2. They cannot be separated
  with this design.
- **Tier A coverage.** 35 questions allocated by sqrt(section tokens). 2 sections were skipped as too short (<50 tokens),
  and 12 small sections got 0 questions because of the budget, not because they were too short. The two big H2s
  (53% of tokens) received 13/35 (37%).
- **Tier B coverage.** 13 of the 15 questions have a gold section. Those 13 land on 8 distinct gold sections, or 15
  if also_acceptable and required_all are counted. **30 of the 46 sections are never labelled**, including every TIER2A section,
  PART1's two methodology notes, and most of CONTEXT "Current state". These are the sections holding most of the
  stale facts, so Tier B does not test the stale-fact sections. The stale-fact axis has its own questions.
  9 of the 13 answerable questions have their gold in README, consistent with Roy writing as a README reader. README "Part 3" alone is
  gold for 4 questions.
- **Non-standard Tier B questions** are scored separately and not averaged into recall:
  - Q2 (unanswerable) and Q6 (unsettled): correct = abstain. Each has a recorded predicted failure passage.
  - Q9 (underspecified_premise): scored best/pass/fail on the generated answer.
  - Q14 (multi_section): strict and lenient both reported. The gap between them measures the shortcut route.
  - Q6/Q10 pair, reported together: the same PART1 Baselines sentence ("The first uses only the destination...") is
    Q10's correct answer and Q6's trap. Retrieval can be right while the reading is wrong, and that is a separate
    failure mode from a retrieval miss.
- **Label readings Roy chose, and the stricter alternative:**
  - Q8 is read as "why SageMaker at all", answered by Part 3 (measure serving latency against the 100 ms frame
    budget). Under the stricter "why SageMaker rather than alternatives" it is unanswerable.
  - Q15 is reading A: prediction vs each new measurement.
  - Q4 excludes README Limitations, because its "isotropic Gaussian" is about the landing-point axis, not the
    position noise.

## Sweep
- Overlap is reported as MEASURED; nominal values go in a footnote.
- The interaction check rests on ONE comparison (the 256 pair). cs1024_matched differs from cs1024 in 2 of 64 chunks
  and is not independent evidence. "No interaction" would be one observation, not a demonstration.
- Model axis cut. Titan v2 only (see operational_findings.md).

## Scoring plan: Tier A vs Tier B (pre-registered 2026-11-05, before any retrieval)
Two Tier A pools from the same generator and the same filters:
  - main   : the 35 sqrt-allocated questions, untouched. Used for (1).
  - top-up : 1 extra question per Tier B-covered section (15), generated separately and told which facts the main
             pool already asked. Used ONLY in (3).
Report three numbers per metric, never one:
  1. Tier A main pool, all questions
  2. Tier B, all retrieval-scored questions (11 standard + B09 + B14 under each rule; B02/B06 scored on abstention only)
  3. Tier A on the 15 sections Tier B covers (gold, also_acceptable or required_all): main-pool questions in those
     sections (at most 14) plus the top-up (at most 15). About 28 after filtering. Gold-only coverage (8 sections) is
     reported as a sensitivity check.
Reading:
  - HEADLINE: (2) vs (3), Tier B against Tier A on the same sections.
  - SECONDARY, indicative only: (1) vs (3). The pools differ, since (3) includes questions targeted at Tier B's
    sections, so this is not a clean coverage comparison, and the write-up says so.

### What this design can detect (computed before any data; scripts/power.py)
Fisher exact, two-sided, alpha 0.05, Tier A matched n=28 vs Tier B n=13, questions treated as independent:

| Tier A recall@5 | min OBSERVED gap reaching p<.05 | TRUE gap detected with 80% power |
|---|---|---|
| 0.6 | 38 pts | 46 pts |
| 0.7 | 41 pts | 48 pts |
| 0.8 | 40 pts | 47 pts |
| 0.9 | 35 pts | 43 pts |
| 1.0 | 23 pts | 31 pts |

Without the top-up (n=14 vs 13), the 80%-power gap is 51-57 pts, or 39 at ceiling. With an unlimited Tier A (n=200) it
is still 37 pts at Tier A 0.8. **Tier B's n=13 is the binding constraint, and no Tier A top-up fixes it.** The true
power is somewhat lower than tabulated, because top-up questions share sections with main-pool questions and are not
independent.

### Rank-based metrics (computed before any data; scripts/power_rank.py, output in logs/power_rank.txt)
Question asked: does using the gold section's rank, instead of binary recall@5, bring the detectable gap down to
something a style difference could plausibly produce?
Decision rule, fixed before computing: a rank-based test becomes the PRIMARY metric for (2) vs (3) only if its
80%-power gap, in recall@5-equivalent points, is <= 20 pts. That 20-point ceiling on a plausible style-only effect
is an ASSUMPTION, not a literature figure.

Tests compared (two-sided, alpha 0.05, n 28 vs 13):
- Mann-Whitney on rank censored at k=5. This is identical to Mann-Whitney on reciprocal rank, since 1/rank is
  monotone and both use the same ties, so it is one test, not two.
- Permutation test on the MRR difference.
- Mann-Whitney on the UNCENSORED rank among all chunks. Exact retrieval ranks every chunk, so this costs nothing.
- Fisher on recall@5, as the reference.

Assumed rank model: log(rank) ~ Normal, sigma 1.0 or 1.5 (sensitivity), Tier B shifted worse. Delta grid step
0.25, so each figure is accurate to within about one grid step (about 5-8 pts).

80%-power gap, as the TRUE recall@5 gap (MRR@5 gap in brackets):

| Tier A r@5 | sigma | Fisher r@5 | MWU censored = MWU on RR | perm MRR | MWU full rank |
|---|---|---|---|---|---|
| 0.6 | 1.0 | 49 (0.23) | 44 (0.21) | 49 (0.23) | 37 (0.19) |
| 0.7 | 1.0 | 46 (0.26) | 46 (0.26) | 46 (0.26) | 38 (0.23) |
| 0.8 | 1.0 | 55 (0.35) | 46 (0.32) | 46 (0.32) | 36 (0.27) |
| 0.9 | 1.0 | 49 (0.43) | 39 (0.37) | 39 (0.37) | 39 (0.37) |
| 0.6 | 1.5 | 49 (0.31) | 46 (0.29) | 46 (0.29) | 37 (0.25) |
| 0.7 | 1.5 | 49 (0.35) | 44 (0.33) | 49 (0.35) | 44 (0.33) |
| 0.8 | 1.5 | 49 (0.42) | 43 (0.38) | 43 (0.38) | 36 (0.34) |
| 0.9 | 1.5 | 49 (0.50) | 35 (0.40) | 35 (0.40) | 35 (0.40) |

**Outcome: the rule is NOT met.** The best rank-based test (Mann-Whitney on the uncensored rank) still needs a true
gap of about 35-44 recall@5 points. It improves on Fisher by roughly 5-13 points, and no test reaches 20.
- recall@5 is NOT replaced as primary.
- **The style hypothesis cannot be tested at this design's scale, whatever the metric.** (2) vs (3) is reported as
  point estimates with n and 95% CIs only: recall@5, MRR, and the median uncensored rank.
- The uncensored rank is the most informative of these for description, and it is reported alongside.

### Paired design on the same facts (computed before generating; scripts/power_paired.py, logs/power_paired.txt)
Proposal: for each of the 13 answerable Tier B questions, generate MC (machine-written, Chinese) and ME
(machine-written, English) about the same gold section and the same fact. The contrasts are within each pair:
- R vs MC: style, with language held constant
- MC vs ME: language, with style held constant
- R vs ME: the combined gap
Section difficulty then cancels out within each pair.

Assumed model on latent log-rank: a shared fact term u ~ N(0, tau^2) plus a question term e ~ N(0, s^2), with
sigma^2 = tau^2 + s^2. Within-pair correlation rho = tau^2 / sigma^2, run at 0.3 and 0.6 as pre-specified.
n = 13 pairs, two-sided alpha 0.05, delta grid step 0.125.

80%-power gap, as the TRUE recall@5 gap (MRR@5 gap in brackets):

| sigma | rho | pA | McNemar r@5 | Wilcoxon full rank |
|---|---|---|---|---|
| 1.0 | 0.3 | 0.6 / 0.7 / 0.8 / 0.9 | 56 / 59 / 58 / 58 | 44 / 43 / 41 / 39 |
| 1.0 | 0.6 | 0.6 / 0.7 / 0.8 / 0.9 | 55 / 56 / 54 / 58 | 33 / 34 / 31 / 29 |
| 1.5 | 0.3 | 0.6 / 0.7 / 0.8 / 0.9 | 55 / 59 / 60 / 58 | 44 / 44 / 43 / 39 |
| 1.5 | 0.6 | 0.6 / 0.7 / 0.8 / 0.9 | 54 / 55 / 55 / 55 | 35 / 35 / 36 / 29 |

MRR gaps for each cell are in logs/power_paired.txt.

The correlation needed to clear the bar (Wilcoxon full rank, pA 0.8):

| rho | sigma 1.0 | sigma 1.5 |
|---|---|---|
| 0.8 | 24 pts | 25 pts |
| 0.9 | 17 pts | 18 pts |
| 0.95 | 12 pts | 14 pts |

**Outcome: the 20-point bar is NOT met at the pre-specified rho (0.3, 0.6).**
- McNemar is worse than the independent-groups Fisher test (54-60 vs 43-55). Only pairs that disagree carry
  information, and 13 pairs give very few of them.
- Wilcoxon on full rank improves on the independent-groups Mann-Whitney only at rho 0.6 (29-36 vs 35-44).
- It clears 20 points only if rho >= ~0.9, meaning two phrasings of the same fact land almost the same
  retrieval rank. Whether that holds is an empirical question, and it is unknowable before the data exists.
- All three contrasts drawn from the same pairs would also need a multiple-comparison correction (e.g. Holm), which
  raises every threshold above these single-test figures.
**Conclusion, derived rather than assumed: at this corpus size, with 13 human questions, the style effect cannot be
tested to the 20-point bar unless within-pair rho is about 0.9 or higher.** The paired design does not become the
primary comparison. The independent-groups plan stays exactly as written.

**Pre-committed reading.**
- A non-significant result means "no gap of at least ~40-47 points was detected". It does NOT mean "no gap".
- A gap that size is about the most this design can see. With Tier A near 0.8, a detectable gap means Tier B recall
  around 0.35 or below, which is near-collapse on Roy's questions.
- A plausible style-only effect is well below that threshold. Any gap large enough to detect would most likely come
  mainly from the language confound (Chinese questions, English corpus), not from question style.
  More questions or a better metric would not change this: the language confound is a bias, not noise, so it does
  not shrink with n.
- So **the style comparison cannot be made as a hypothesis test at this scale.** The A/B gap is reported
  descriptively, as point estimates with n and 95% CIs, and is not claimed as a style finding either way.

**The only lever is more Tier B questions.** At Tier A 0.8, Tier B n=30 still needs 37 pts (Tier A 28) or 31 pts
(Tier A 60). n=60 per side needs 26 pts, and n=100 per side needs 19 pts. Whether to write more is Roy's decision,
to make once the first numbers are in front of him.
  - If the gap survives on the matched subset, it is about question style. If it collapses, it was mostly coverage,
    and the write-up says so instead of claiming the style result.
  - With n of about 13-14 per side, one question moves recall@5 by about 7 points. Every number is reported with n
    and a bootstrap 95% CI. If the CIs overlap, "survives" and "collapses" are both unsupported, and the write-up
    says the subset is too small to decide.
  - The matched subset controls coverage only, not language. Tier A is English, Tier B is Chinese, so (3) vs (2)
    still carries the language confound.

## Corpus
- Stale statuses in CONTEXT.md's undated tier table, the only unmarked status-type stale facts in the list:
  - SF10 (confirmed): Tier 2 "not started" (CONTEXT.md:94), yet Part 3 is complete. Predicted failure for B01/B07/B08.
  - SF11 (candidate, pending Roy's confirmation): Tier 1 "Learned-model part (Task K) not started" (CONTEXT.md:93),
    yet K1-K5 are reported in README Part 2.

## Tier A main pool, as generated (2026-11-06, Sonnet 4.6)

- **Counts.** 35 requested, 35 generated, **33 kept**.
- **Drops.** 2 were dropped: the generator's evidence quote was not contiguous. One joined two spans with "…", the
  other skipped table rows.
- **Matcher errors.** The first pass dropped 2 more because of a matcher bug: `norm()` did not strip blockquote
  markers or line-wrap whitespace after "/". The bug was fixed generally and the filter re-run over all 35. The fix
  changed only those two verdicts, and both then passed the verifier. The filter-error count on this run is
  reported as 2 of 35. Pre-fix files are kept as `eval/tier_a.pre_normfix.jsonl` and `eval/tier_a_dropped.pre_normfix.json`.
- **Verifier positive control** (`scripts/verifier_control.py`, `eval/verifier_control.jsonl`). 6 of 6 should-fail
  questions were rejected:
  - 4 kept questions shown with an unrelated section (answer key checked absent beforehand),
  - 2 questions the corpus cannot answer, one of them a near-miss shown with the Part 3 cost section.

  So 0 of 33 verifier rejections is evidence that the generator is good, not that the screen is broken. **Limit:**
  the controls test gross mismatch. They do not test partially answerable questions, or questions needing a fact
  from a second section, apart from the one near-miss.
- **Question-quality observation (kept, not dropped on taste).** The CONTEXT "The framing" question asks about "the
  project's resume line". It is answerable from that section, but it targets meta-text about the author's resume,
  not project content.
- **Cost.** $0.585 generation plus $0.057 control. The estimate was $0.33: per-call input averaged about 2,030
  tokens, because each call carries the section plus the tool definition, and the verifier sends the section again.

## Caveat for Tier B B02 and B06, and for every abstention rate (2026-11-06)
The answer prompt (mitigations/stale_prompt.json) explicitly tells the model to say "the documentation provided
does not say" when the excerpts lack the answer. Abstention is therefore measured under an abstention instruction.
Every abstention rate, including how B02 (unanswerable) and B06 (unsettled) are answered, is an **upper bound on
unprompted abstention**. Real systems do instruct abstention, so the setting is realistic, but the caveat belongs
next to those results.

## Stale-fact mitigations: findings already fixed before any answer (2026-11-06)
- **Recency, a failed attempt, reported as such.** We tried to separate "the recency technique doesn't help" from
  "the dates carry no information" by running git-commit dates alongside content dates derived from `git blame` on
  the current-value lines. It could not be done. The repo's whole history is a two-day publication burst
  (2026-11-02/03), and blame dates are publication dates too. CONTEXT.md, which holds most stale values, ties for
  newest under both derivations, and TIER2A_RESULTS.md, which holds SF9's correction, is oldest under both.
  **Documents published in one burst carry no recency signal in version control, so date-based mitigations have
  nothing to work with.** Only the git-date condition is run, and a failure there is not attributed to the technique.
- **The corrections document is not reached** (logs/corrections_rank_diagnostic.json). Of 102 chunks, the
  best-ranked corrections chunk for the 11 facts sits at rank 11-73, median 36. None reaches top-10, so a larger k
  (the sweep's 10) would not fix it. The document is far from the question space, not marginal. The only top-10
  hit is X1 (rank 6), whose question contains "corrected" and which is not in the document. That is word overlap,
  not content. A plausible cause, stated and NOT tested: each 512-token chunk mixes five or six entries, which dilutes
  every entry's embedding. "One entry per chunk" is the untested next step. The template's shorthand also probably
  lowers retrievability (provenance file). Both biases run against the intervention.
- **Retrieval-limited facts.** At baseline, SF3, SF10 and SF11 retrieve only old-value lines. Propagation on those is
  a retrieval failure, so headline rates are also reported without them.

## Step 2 outputs (2026-11-06, Sonnet 4.6)
- **Top-up pool** (eval/tier_a_topup.jsonl): 15 of 15 kept, 0 dropped, $0.277. Used only in analysis (3).
- **Paired set** (eval/tier_a_paired.jsonl, scripts/gen_paired.py): 26 generated, **20 kept**, $0.397 + $0.038.
  - The generator saw the fact (Tier B expected_answer) and the gold section, never Roy's wording.
  - Drops (6), none replaced:
    - B09 MC and ME: quote joins spans with "…".
    - B07 MC: quote drops a table pipe.
    - B14 MC and ME: the verifier finds σ = 2.0 not in the gold section alone. B14 needs its second section, as
      pre-stated.
    - B15 MC: the verifier finds the Q/R balance only partly stated.
  - **Matcher bug fixed (third instance, same rule as before).** At markdown table-row boundaries the section text
    reads "| |", so quotes that run contiguously across rows never matched. `norm()` now collapses repeated pipes, on
    both sides. Re-filtering all 76 generated questions (main 35, top-up 15, paired 26) changed exactly 3 verdicts,
    all in the paired pool and none in main or top-up. All 3 then passed the verifier. Filter-error count on the
    paired pool: 3 of 26. Pre-fix files are kept as `*.pre_normfix.*`.
  - **Usable structure:**
    - complete triads (R, MC, ME): **9** (B01 B03 B04 B05 B08 B10 B11 B12 B13)
    - R-ME pairs: **11** (those 9 plus B07, B15)
    - R-MC pairs: **9**
  - Power was computed at n = 13 and did not clear the bar even then. At 9 to 11 pairs the comparison is
    descriptive only.

## Stale-fact run: interpretation notes (2026-11-06; results in reports/stale_results.md)
- **MIXED carries most of the "propagation"** (33 MIXED answers out of 132 fact answers). POST-HOC and descriptive
  only (no rule change): 17 of the 33 mention "week 1" somewhere. 12 of those are SF7, where every arm and
  condition says "3.5% on full data, while on the week 1 sample it was 4.6%". That is arguably a correct, scoped
  answer, which the frozen rule counts as propagated because revision 2 removed "week 1" as a marker. Four SF4
  answers scope the values in the NEXT sentence ("These figures are from week 1 only"), and the rule requires the
  marker in the same sentence. Both are the conservative bias chosen in advance. The headline remains the rule's
  output (section 6). S1 (MIXED -> neither) is the bound in the other direction, and Roy's blind audit
  (eval/stale_audit_blind.jsonl, 58 answers) measures which is closer.
- **Order changes under sensitivity lines** (pre-registered as a main-text finding):
  - Opus, S1: the exclude_context advantage (5 -> 2 propagated) disappears completely (1/1/1). It was made
    entirely of MIXED answers.
  - Haiku, S1 and S2: the order among the three conditions changes. Every Haiku difference is 1 fact, within noise.
- **Noise floor at temperature 0 differs by arm.** In the identical-prompt repeats:
  - Haiku: 0/12 answers textually different, 0/12 class changes (and 0/0 in the stability check).
  - Sonnet: 5/12 textually different, 0/12 class changes.
  - Opus: 7/12 textually different, **1/12 class change**.

  So a 1-fact difference on Opus is within noise.
- **exclude_context works where predicted, and only there.** Sonnet and Opus fix SF10 and SF11 (old site only in
  CONTEXT.md). Haiku's SF5 BREAKS (CURRENT -> PROPAGATED), because SF5's current value is also in CONTEXT.md, so
  removing the file removes the correction too. Excluding a file is not a targeted mitigation.
- **recency_git does nothing measurable** (0-1 fact changes per arm), consistent with the dates carrying no signal.
- **X1: CORRECT in all 12 cells.** No arm invents a replacement for the 0.23 figure, under an explicit abstention
  instruction.

## Hand audit, first scoring (2026-11-06; reports/audit/agreement.md; 2 blocks in worksheet 1 still blank)
- **Agreement on headline buckets:**
  - worksheet 1 (census of MIXED/OTHER): 5/34 = 0.15, kappa -0.01
  - worksheet 2 (random rest): 15/18 = 0.83
  - provisional population estimate: about 0.65, **below the 0.85 threshold**

  Per section 6, the stale-fact results are labelled **rule-dependent**, the rule's numbers stay the headline, and
  Roy's hand-labelled rates are shown beside them. X1: 4/4 agree.
- **Where they disagree, by fact (key side; Roy stays blind):**
  1. SF7, SF4 and SF8, MIXED -> Roy "current" (16 answers): the predicted conservatism. The answer scopes the old
     value ("on the week-1 sample it was 4.6%") without a listed marker in the same sentence. Roy reads these as
     conveying the right value.
  2. SF10, MIXED -> Roy "neither" (7) and "propagated" (2). SF11 MIXED splits 3 propagated / 3 current / 1
     neither. Roy and the rule disagree on hedged status answers.
  3. **SF3: an instrument error found by the audit, not a judgement call.**
     - The answers give the current values ROUNDED ("~0.3 yd at 1.9 s", "past 1.5 yd by 3 s"). The frozen `current`
       patterns accept only 0.31 and 1.51, so answers carrying both values were classed PROPAGATED or OTHER. Roy
       labelled all 5 "current".
     - The same answers show that SF3's **current value IS retrieved** at baseline, through a sentence outside the
       `current_sites` listed in stale_facts.json. So the pre-run "retrieval-limited" label for SF3, and its
       exclusion from the 8-fact headline, rest on an incomplete site list.
     - As pre-registered, the patterns are NOT retuned for this run. Both errors are reported as measured
       limitations of the instrument.
- **Final scoring (all 58 labelled):**
  - worksheet 1: 5/36 = 0.14, kappa -0.01
  - worksheet 2: 15/18 = 0.83
  - **population estimate 0.64, below 0.85, so the results are rule-dependent**
  - X1: 4/4
- **Roy's rates, shown beside the rule's (section 6).** Stratified estimate over the 132 fact answers (census of 36
  plus a sample of 18 from the other 96):
  - **propagated ≈ 5 (4%), against the rule's 52 (39%)**
  - current ≈ 119 (90%)
  - neither ≈ 8 (6%)

  All 5 answers Roy labels propagated are **SF10 or SF11**, the two UNMARKED status facts (Haiku, Sonnet, Opus;
  various conditions).
- **Reading.** The rule's 39% is driven by its conservative sentence-level marker requirement and by SF3's pattern
  gap. On Roy's judgement, models rarely leave a reader with a superseded value when the corpus marks the
  correction. Where propagation does happen, it is on the unmarked facts, which is the pre-registered hard case.
  The second number is an estimate from a stratified sample, not a census: the 96 non-fragile answers are
  represented by 18.
