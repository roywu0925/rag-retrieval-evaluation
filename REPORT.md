# Retrieval evaluation over a single project's documentation: one result, two unanswerable questions, one instrument failure

**Corpus:** the five Markdown documents of [uwb-trajectory-degradation](https://github.com/roywu0925/uwb-trajectory-degradation),
frozen at commit 9bfc7b1 (33,757 tokens, 46 labelled sections).
**Pipeline:** Titan v2 embeddings and exact cosine retrieval in numpy (no managed retrieval service). Answers come
from Claude on Amazon Bedrock. No LLM judge was used anywhere.
**Cost:** $4.46 of a $20 budget.

## What this study found, stated up front

The study set out to answer three questions. **One of them it answers. Two it cannot answer at this scale, and it
says what scale would be needed.** Along the way, the design's own validation step caught **its classifier being
wrong on the cases that drove a headline number.**

1. **Measured: generated eval questions overstate retrieval quality, by somewhere between 9 and 58 points.**
   - On the sections Roy's own questions cover, LLM-generated questions retrieve their gold section more often than
     his. The gap is **somewhere between +9 and +58 points** (95% CI). This study cannot tell which end is true.
   - The point estimate (+31) is **likely larger than the true gap.** The design was pre-registered as underpowered,
     and a significant result from an underpowered design is expected to be inflated (Type M error). **A true gap
     anywhere from 5 to 20 points produces significant estimates averaging 26-31, so the point estimate carries
     almost no information about the true effect.**
   - A secondary, paired cut of the same human questions suggests that style and language each contribute. It is
     not significant on its own.
2. **Not answerable here (pre-registered questions, with the numbers that would be needed):**
   - **Which chunking/retrieval knob matters.** Retrieval sits at 88%, and every knob effect falls inside its
     confidence interval. A 5-point effect would need about 160-400 questions.
   - **Which stale-fact mitigation works.** With 11 stale facts, exact McNemar needs 6 facts fixed and none broken;
     on the human labels only 2 facts propagate at all.
3. **An instrument failure, found because the design required an audit.**
   - The deterministic classifier chosen over an LLM judge for objectivity was **wrong on 31 of the 36 answers that
     drove its headline**. Its pre-registered headline (39% of answers repeat a superseded value) is about ten times
     the human-audited estimate (4%, 95% upper bound 17%).
   - This is the most transferable result here. Most evaluation work never validates its own classifier, so it
     cannot know whether this has happened to it.

**Points 2 and 3 are results, not excuses, because they were committed to in advance.**
- Every power analysis was written **before any result existed**: scripts/power*.py, recorded in
  reports/writeup_notes.md before the first retrieval.
- The stale-fact rule, its patterns, its prompt and its mitigations were hash-frozen before the first answer:
  reports/stale_fact_rule.md, freeze log 2026-11-06T22:57:26Z.
- The audit's sample, threshold and reporting rule were fixed before any answer was labelled.

So "cannot be answered" is a prediction that held, and "the classifier failed" is a measurement the design asked for.

---

## 1. The measured result: the generated-vs-human eval-set gap

Full write-up: [reports/finding_b_eval_gap.md](reports/finding_b_eval_gap.md).

**The pre-registered comparison** (fixed 2026-11-05, before any retrieval) is generated questions on the sections
Roy's questions cover, set (3), against Roy's questions, set (2). Recall@5 at the base configuration, with Wilson 95%
intervals:

| question set | n | recall@5 |
|---|---|---|
| (3) Generated (Sonnet 4.6, English), on the sections Roy's questions cover | 27 | 100 [88, 100] |
| (2) Roy's own (verbatim Chinese), strict | 13 | 69 [42, 87] |

**Headline: the gap is somewhere between +9 and +58 points** (Newcombe 95% interval for the difference; Fisher exact
p = 0.008). The two ends support different conclusions. +9 is a modest eval-set bias. +58 means a generated-only
eval set would badly misjudge this retriever. This study cannot separate them.

**The point estimate (+31) should not be quoted as the size of the gap.** The pre-registered power analysis said
this design needs a true gap of about 40-47 points for 80% power. A significant result from a design that
underpowered is expected to overstate the effect, because only samples that land large clear the threshold.
- A retrodesign at this n (scripts/retrodesign_ab.py) assumes generated questions near ceiling, as observed.
- Under that assumption, any true gap from 5 to 20 points produces significant estimates that **average 26-31
  points**. An observed +31 is therefore what this design returns whether the true gap is 5 or 20.
- This is the same selection mechanism as the optimism in the NFL project's model selection.

Scoring Tier B's multi-section question leniently gives +23 [+4, +50]. The pre-registered secondary comparison,
generated questions over the whole corpus against Roy's (pools that differ in coverage, so indicative only), gives
+19 [−5, +46], which is not significant.

**Secondary, and not a confirmation: the paired decomposition.** For each of Roy's questions, a Chinese (MC) and an
English (ME) question were generated on the same fact and section, with the generator never shown his wording. This
was pre-registered as an addition to the main comparison, never as a replacement for it.

| contrast (paired, recall@5) | n | difference | exact McNemar |
|---|---|---|---|
| Style (Roy vs generated, both Chinese) | 9 | −11 [−47, +28] | p = 1.0 |
| Language (generated Chinese vs English) | 9 | −11 [−43, +20] | p = 1.0 |
| Combined (Roy vs generated English) | 11 | −27 [−57, +4] | p = 0.25 |

None of these is significant, and they **do not independently confirm the headline**. Roy's questions are the human
side of both cuts: 11 of the 13 in set (2) are also the "Roy" side here. The paired cut says only that, on these 9-11
facts, the human-vs-generated difference has no sign of being purely stylistic or purely linguistic. In 3 pairs the
generated question hits where Roy's misses, and the reverse never happens.

**Why the decomposition stays descriptive.** About 60 human questions per side would be needed to test a gap in
this range. Writing them was declined on purpose: at that number they would stop being questions Roy would
naturally ask, which is the thing Tier B measures. The language component is a bias that more questions would not
remove.

## 2. Two pre-registered questions this corpus cannot answer

### 2a. Which retrieval knob matters

Full write-up: [reports/finding_a_knobs.md](reports/finding_a_knobs.md).

Nine one-factor-at-a-time configs varied chunk size (256/512/1024), overlap (0/8/23% measured) and top-k (3/5/10).
On the generated questions, no change moves recall beyond its CI. The largest is top-3 at −9 points, mostly because
there are fewer slots. A matched-overlap check found no chunk-size × overlap interaction, but that check is one
observation.

**The number needed:** with 29 of 33 questions already retrieved, no improvement is detectable at this n (power
0.005 for a 5-point gain). About **160 questions** would be needed if a knob only helps, and about **400** with
realistic churn. Alternatively, an eval set hard enough to start near 60% would need far fewer. What can be said
is that at the scale of one project's documentation, these chunking choices do not matter measurably.

On Roy's questions, ranking the knobs by raw recall disagrees with ranking them by recall above random retrieval.
That disagreement was pre-registered as reportable, and its cause is large gold sections (top-10 random retrieval
already scores 42%). It is reported, not interpreted.

### 2b. Which stale-fact mitigation works

Full write-up: [reports/finding_c_stale_facts.md](reports/finding_c_stale_facts.md).

**Design:** 11 facts the corpus states twice (an old and a corrected value) × 4 conditions × 3 models (Haiku 4.5,
Sonnet 4.6, Opus 4.6), 144 answers. The four conditions are baseline, excluding the file with most old values,
recency dates, and a corrections document.

**The number needed:** exact McNemar over 11 facts rejects only if at least 6 are fixed and 0 broken. This was
computed before running, so mitigation results were declared descriptive by design. Under the frozen rule, the best
mitigation fixed 3 and broke 0 (p = 0.25). Under the human labels the question nearly disappears: **only 2 of the 11
facts propagate at all.** Testing mitigations needs a corpus with at least 6, and realistically about 30, facts that
actually mislead.

Two mitigations failed for reasons found **before** any answer:
- **Recency dates carried no information.** The repository's whole history is a two-day publication burst, so
  git dates rank the main stale file as tied-newest. Documents published in one burst carry no recency signal in
  version control, so date-based mitigations have nothing to work with. A second date derivation meant to
  separate "the technique fails" from "the dates are bad" could not be built, and that failed attempt is reported.
- **The corrections document was never retrieved.** For the 11 facts, its best rank was 11-73 of 102, so even
  top-10 would not reach it.

**What the stale-fact data does show:**
- **All 5 human-labelled propagations are on the 2 facts the corpus never marks as corrected,** in all three models.
- **Within those facts, the same model answers wrongly when retrieval returns only the old lines, and correctly
  when an intervention swaps in the current lines.** The context decides, not the model.
- **The limit:** this corpus has no unmarked fact whose correction is also retrieved, so "unmarked" cannot be
  separated from "not retrieved".

## 3. The instrument failure: a deterministic classifier, validated, and wrong

Full write-up: [reports/finding_c_stale_facts.md](reports/finding_c_stale_facts.md); data in
[reports/audit/agreement.md](reports/audit/agreement.md).

**The classifier.** The project ruled out an LLM judge. Stale-fact answers were classified instead by a
pre-registered, hash-frozen string and number matcher, tested against 44 hand-written cases before the freeze. The
pre-registration also required a blind human audit:
- every answer in the classifier's fragile classes (36),
- a random 20% of the rest,
- an agreement threshold of 0.85,
- and a rule that the classifier's output stays the headline either way.

**The audit.**
- On the 36 answers driving the classifier's 39% propagation headline, it agreed with the auditor on **5**.
- Population-weighted agreement was 0.64.
- Kappa is degenerate on both strata (one stratum is selected by the classifier's own class, the other is 90% one
  label), so raw agreement and the confusion matrix are reported instead.
- The human-label estimate of propagation is **4% (5/132; 95% upper bound 17%)**, against the classifier's 39%.

**The diagnosis traces to three documented choices**, each with a stated rationale, all made before any answer
existed:
1. A correction marker had to appear in the same sentence as the old value.
2. "Week 1" was removed as a marker, so that "0.029 on week 1 data" could not escape as flagged. It was proposed by
   the assistant and approved by Roy. This one choice turned 12 correct, scoped answers ("3.5% on full data; on week
   1 it was 4.6%") into propagations.
3. The numeric patterns did not anticipate rounding ("about 0.3 yd" for 0.31).

The patterns were not retuned. The audit stands as the measurement of the classifier's error, which is what it was
pre-registered to be.

**Five instrument failures in all, and no automated test caught any of them.** The classifier above had passed
all 44 of its constructed test cases. Four of the five were found only by reading output by hand:
1. **The stale-fact classifier**: found by the pre-registered audit (the reading the design required).
2. **The evidence-quote matcher**, with three layout bugs (blockquote markers, line wraps, table-row pipes) that
   falsely dropped 5 generated questions: found by reading the dropped quotes by hand.
3. **An incomplete current-value site list for one fact (SF3)**, which wrongly marked it as unretrievable and
   excluded it from a headline rate: found by reading the answers behind an audit disagreement.
4. **The abstention detector**, which read only English and missed a Chinese abstention, so B06 is 9/9, not 8/9:
   found by reading one answer while writing this report.
5. **The headline interval.** The instruction to "report the interval" did not say how to compute it. The
   percentile bootstrap first used has zero variance on the 27/27 generated set, which made the headline interval
   too narrow ([+8, +54]; the score interval is [+9, +58]) and gave the paired interval an artefactual upper limit
   of exactly 0. **Specified by Claude (the planning instructions); caught by Claude Code during execution**, by
   reading a [100, 100] interval and asking how it was produced.

**Methodological finding.** We avoided an LLM judge in favour of a deterministic, pre-registered string
classifier, on the grounds that it is objective. On the cases that mattered it disagreed with a human auditor on 31
of 36. **Determinism is not accuracy, and an eval classifier needs its own validation.** Here the validation was
pre-registered, which is the only reason a 10× error was caught rather than published.

## 4. Operational findings (Amazon Bedrock, us-west-2)

Full write-up: [reports/operational_findings.md](reports/operational_findings.md).

- **Model access.** The `agreementAvailability` status read NOT_AVAILABLE both for models that were callable and
  for models that were not, so it predicted nothing. The real blockers were missing Marketplace permissions on the
  IAM user, and then account eligibility: the Claude 5.x models and Opus 4.7+ were denied with "contact AWS Sales".
  A 1-token probe of every listed model was the only reliable check.
- **The embedding-model axis was cut.** Cohere's Marketplace entitlement failed intermittently, so the study ran on
  Titan v2 only.
- **Batch inference was not used.** It is not offered for the 5.x models, and Haiku 4.5 batch costs 5× Haiku 5.5
  on-demand.
- **Cost estimation.** The one estimate made from assumed tokens missed by 77%. Every estimate made after measuring
  one real call landed within 5%.
- **Run-to-run noise at temperature 0 differs by model.** On identical prompts:

  | model | answers textually different | answers changing class |
  |---|---|---|
  | Haiku 4.5 | 0/12 | 0/12 |
  | Sonnet 4.6 | 5/12 | 0/12 |
  | Opus 4.6 | 7/12 | 1/12 |

## 5. Notes on process

[reports/notes_on_process.md](reports/notes_on_process.md). Three times in this project, a claim that felt right had
no source: résumé numbers, the cause of the Bedrock failures, and four claims in one write-up instruction. Each time
the correction came from a file, a log or a real call, never from recall.

## Pending

- **B09** (the underspecified-premise question): Roy's best/pass/fail score on the generated answers.
  [reports/audit/B09_worksheet.md](reports/audit/B09_worksheet.md).

## Reproducing

All billed calls are logged under logs/. Embeddings are cached in cache/, and the indexes are in indexes/.
Re-running the analyses needs no API calls:

```
.venv/bin/python scripts/analyze_sweep.py      # reports/sweep_results.md
.venv/bin/python scripts/analyze_stale.py      # reports/stale_results.md
.venv/bin/python scripts/score_audit.py        # reports/audit/agreement.md
.venv/bin/python tests/test_hit_rule.py && .venv/bin/python tests/test_cache.py && .venv/bin/python tests/test_stale_classify.py
```

Generation and answer runs (`scripts/gen_tier_a.py`, `gen_paired.py`, `run_sweep.py`, `run_stale.py`) refuse to
overwrite existing outputs. `run_stale.py` also refuses to run unless every hash in the freeze log matches.
