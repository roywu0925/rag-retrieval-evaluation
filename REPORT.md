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

1. **Measured: generated eval questions overstate retrieval quality.**
   - On the sections Roy's own questions cover, LLM-generated questions retrieve their gold section 31 points more
     often than his [95% CI +8, +54].
   - On paired questions about the same facts, the gap splits roughly evenly between question style and question
     language.
   - These are point estimates with intervals, not a test.
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

Recall@5 at the base configuration (512-token chunks, top-5):

| question set | n | recall@5 |
|---|---|---|
| Generated (Sonnet 4.6, English), whole corpus | 33 | 88 [76, 97] |
| Roy's own (verbatim Chinese) | 13 | 69 [46, 92] |
| Generated, on the sections Roy's questions cover | 27 | **100** [100, 100] |

On exactly the sections a human user asked about, a generated-only eval set would have scored this retriever as
perfect, while about a third of the human questions missed.

The **decomposition** comes from generating a Chinese and an English question for each of Roy's questions, on the
same fact and section, with the generator never shown his wording. It gives three paired contrasts:
- **Style** (Roy vs generated, both Chinese): −11 points [−44, +22], n = 9.
- **Language** (generated Chinese vs English): −11 [−33, 0], n = 9.
- **Combined:** −27 [−55, 0], n = 11.

No pair goes the other way. **Why it stays descriptive:** the power analysis, done in advance, needed a 40-47 point
gap for a test, and about 60 human questions per side would be needed to test a 27-point one. Writing those was
declined on purpose. At that number they would stop being questions Roy would naturally ask, which is the thing
Tier B measures. The language component is a bias that more questions would not remove.

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

**The smaller versions of the same lesson, all found the same way, by checking an instrument's output by hand:**
- three layout bugs in the evidence-quote matcher (blockquote markers, line wraps, table-row pipes), which falsely
  dropped 5 generated questions;
- an abstention detector that read only English and missed a Chinese abstention;
- an incomplete site list that wrongly labelled one fact as unretrievable.

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
