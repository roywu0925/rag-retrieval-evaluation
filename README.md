# Retrieval Evaluation of a RAG Pipeline over Technical Documentation

A measurement study, not a product. Three questions were asked of a RAG pipeline
built on Amazon Bedrock. One is answerable; two are not, and are reported with the
sample sizes they would require. The most useful finding was none of the three:
the study's own measuring instrument turned out to be wrong.

Total compute cost: **$4.46**.

## The headline finding: the measuring instrument was broken

One axis of the study needed to decide, for each generated answer, whether it had
repeated a superseded number from the corpus. A deterministic string-matching
classifier was chosen over an LLM-as-judge *specifically* because it is objective,
cheap, and reproducible. It passed all 44 of its own constructed test cases.

A blind hand-audit of 58 answers found:

| | |
|---|---|
| What the classifier reported | **39%** of answers propagated a stale value |
| What hand-labelling found | **4%** (95% upper bound 17%) |
| On the decisive cases | the rule was **wrong on 31 of 36** |

Agreement between the rule and the hand labels was **0.64**, below the **0.85**
threshold registered before the audit ran. Per the pre-registered rule, the
classifier's figure remains the headline but is labelled rule-dependent, with the
hand labels reported beside it.

Inspecting the 31 disagreements separates three defects in the rule from a
residue of genuine judgement differences:

| Cases | Cause |
|---|---|
| 12 (SF7) | "week 1" had been removed from the list of supersession markers |
| 4 (SF4) | the marker had to appear in the same sentence as the number, and the scoping sat in the sentence after it |
| 3 (SF3) | the numeric patterns matched exact values only, so answers that rounded ("about 0.3 yd") were missed |
| 11 (SF10, SF11) | the rule and the hand labels simply judged differently |
| 1 (SF8) | — |

The SF7 group is the clearest. This is a real answer (Sonnet, baseline
configuration), and the rule counted it as propagating a stale value:

> "Only 3.5% of tracks survive to the 3-second horizon on the full 18-week
> dataset (394 of 11,254 tracks), while on the week 1 sample alone it was
> 4.6% (24 of 526 tracks)."

— correct, explicitly scoped, and naming the denominator of both populations.

**The transferable lesson is not about RAG.** The deterministic choice was made
because it looked like the more rigorous option, and it was wrong on roughly nine
out of ten of the cases that mattered. Determinism is not correctness, and an
evaluation classifier needs its own validation. Most evaluation work does not run
this step, and so never finds out.

## The three questions

| Question | Outcome |
|---|---|
| Do machine-generated eval questions overestimate the system, relative to hand-written ones? | **Yes. By 9 to 58 percentage points.** The study cannot apportion the gap between question style and language |
| Which retrieval knob matters most (chunk size / overlap / top-k)? | **Not answerable at this scale.** Retrieval sits at an 88% ceiling and every effect falls inside its interval. Detecting a 5-point effect needs 160–400 questions |
| Do the stale-fact mitigations work? | **Not answerable at this scale.** With 11 superseded facts, an exact test needs "6 fixed, 0 broken" |

Single strongest piece of evidence for the gap: for one fact, the gold section
ranks **58th** when the question is asked by hand in Chinese, and **1st** in both
machine-generated versions — including the machine-generated *Chinese* one. That
case points at question style rather than language.

### What the gap cannot be decomposed into

A split into question style and language was registered as a secondary analysis.
It is not significant: style −11 points [−47, +28], language −11 points [−43, +20].
Both intervals cross zero, so the study does not support attributing the gap to
either one.

### On the reported interval

The headline gap is reported as an interval, **+9 to +58 points**, not as its point
estimate of +31. The design was pre-registered as able to detect 35–47 points; a
result that clears a significance threshold in an underpowered design is
systematically inflated (Type M error). A lower bound of +9 and an upper bound of
+58 support materially different conclusions, and this study cannot distinguish
between them.

## What makes the numbers checkable — and where it falls short

Three mechanisms, stated with their actual coverage rather than their intent:

- **Pre-registration, applied unevenly.** For the eval-set gap and the stale-fact
  mitigations, the detectable effect size was computed and written down before the
  results existed; the mitigation question was predicted unanswerable in advance,
  and that prediction held. **The knob question had no power analysis before the
  sweep ran** — its 88% ceiling and the 160–400 figure were computed afterwards,
  while writing up. The difference matters: a prediction that holds is evidence,
  an explanation found afterwards is not.
- **Freezing, partial.** The classification rule and the match patterns are
  recorded by hash, and `scripts/run_stale.py` refuses to start on a mismatch. The
  corpus has recorded sha256 checksums in `corpus/SOURCE.txt`, **but no script
  verifies them**, and the sweep and generation scripts check no hashes at all.
  This is a gap, not a guarantee.
- **Audit.** 58 blind hand labels against the automatic classifier. This was the
  only mechanism that caught the broken instrument.

Five instrument failures were found in total. **Four of them were found by reading
raw output by hand**, not by automated tests. The most pointed one: a study whose
entire hand-written question set is in Chinese shipped an abstention detector that
recognised only English refusals.

## Setup

| | |
|---|---|
| Corpus | 5 Markdown files, 33,757 tokens, 46 labellable sections, frozen at commit `9bfc7b1` |
| Embeddings | Amazon Titan Text Embeddings v2, 1024-d |
| Retrieval | exact cosine over a dense matrix in NumPy — no vector database |
| Generation | Claude Haiku 4.5, Sonnet 4.6, Opus 4.6 via Amazon Bedrock |
| Sweep | 9 configurations, varying one setting at a time from a base (chunk size, overlap, top-k) — not a factorial grid |
| Questions | 33 machine-generated (English) + 15 hand-written (Chinese) |
| Stale facts | 11 known-superseded values, plus 1 hallucination probe, across mitigations and 3 models |

**A vector database was deliberately not used.** At roughly 100 chunks, an
approximate index's recall error would mix into the very quantity being measured.
The independent variable and the measuring instrument must not be the same
component.

**The corpus is documentation from the author's own separate project.** That was a
practical choice, for two reasons: the content is understood well enough to judge
answers correct or incorrect, and it contains a batch of numbers that are known to
have been superseded — material that is hard to obtain otherwise.

## What can and cannot be concluded

**Can:**

1. Machine-generated evaluation questions overestimate retrieval performance on
   this corpus by 9 to 58 points.
2. **What is in the context decides whether a stale value is repeated, not which
   model reads it.** All five answers hand-labelled as propagated occurred where
   retrieval returned only the superseded value. The effect cannot be narrowed to
   retrieval specifically: in this corpus, "the correction was not retrieved" and
   "the correction was not marked" always occur together, and no case separates
   them. The converse does not hold strictly either — for SF11, 3 of 7 answers
   were labelled current even where retrieval returned only old-value lines.
3. Evaluation classifiers require their own validation. Determinism is not
   correctness.
4. At this scale, chunking parameters have no detectable effect — reported together
   with the sample size that would be needed to detect one.

**Cannot:**

| Not supported | What the data actually supports |
|---|---|
| "Chunk size does not matter" | Not detectable at this scale |
| "The mitigations do not work" | Not testable at this sample size |
| "The gap is 31 points" | 9 to 58 points; a point estimate under low power is inflated by construction |
| "The gap is half style, half language" | Neither component is significant; the gap cannot be apportioned |
| "Retrieval is what causes propagation" | Retrieval and marking are confounded in this corpus; only "the context, not the model" is supported |

## Repository layout

| Path | Contents |
|---|---|
| `corpus/` | Frozen corpus snapshot, with source commit and checksums |
| `rag/` | Pipeline: chunking, embedding, indexing, section registry, stale classifier |
| `eval/` | Question sets, gold labels, audit keys |
| `scripts/` | Index builds, sweeps, runs, power calculations, scoring |
| `reports/` | Findings, the pre-registered rule, the audit worksheets, operational notes |
| `mitigations/` | Correction documents, recency metadata, prompt variants |
| `logs/` | Raw run logs and per-call records |
| `probe/` | Bedrock model-availability investigation |
| `tests/` | Unit tests for the hit rule, the cache, and the stale classifier |

Full write-up: [`REPORT.md`](REPORT.md), which also holds the commands to
reproduce the results.
Individual findings: [`reports/finding_a_knobs.md`](reports/finding_a_knobs.md),
[`reports/finding_b_eval_gap.md`](reports/finding_b_eval_gap.md),
[`reports/finding_c_stale_facts.md`](reports/finding_c_stale_facts.md).
The audit: [`reports/audit/agreement.md`](reports/audit/agreement.md).
Operational notes from working against Bedrock:
[`reports/operational_findings.md`](reports/operational_findings.md).
Post-publication edits to recorded artifacts: [`REDACTIONS.md`](REDACTIONS.md).

The embedding cache is committed, so retrieval results can be reproduced without
re-paying for embeddings.
