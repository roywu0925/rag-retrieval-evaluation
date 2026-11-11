# Notes on process

**How this study was done.** This study was carried out with AI assistance for planning and implementation. The author set the scope and research questions, made the design decisions, performed the 58-answer hand audit that the stale-fact results depend on, and is responsible for the conclusions.

- **Checking beat remembering, three times.**
  1. In one instruction about the stale-fact write-up (2026-11-06), I made four claims that the record or the data
     did not support:
     - a **misattributed decision**: I described the removal of "week 1" as a marker as made against a flagged
       risk, when the risk flagged at the time was the opposite one;
     - an **overstated statistical reading**: "performed at chance", on a stratum where kappa is degenerate;
     - a **confounded causal claim**: "the marker, not the model", when marker and retrieval coincide;
     - an **extrapolation without its interval**: "near zero where marked", which omitted 14 unaudited
       rule-PROPAGATED answers on marked facts and the 17% upper bound.

     All four were caught by checking against the files, not against memory.
  2. It is the same failure mode as my résumé numbers: assertions that felt right and had no source. Those
     included an 8.6x with no output behind it, an 11% that regenerates to 11.5%, a ~4,000 km that is ~3,500, and a
     $0.12/hr that is $0.115/hr in the price list.
  3. It is also the same failure mode as the first explanations of the Bedrock access failures. The model agreement
     was blamed for the Cohere errors (operational_findings.md OF1, withdrawn to UNRESOLVED), then a missing
     per-model subscription for Sonnet 5.5 (OF3, corrected the same day). A 1-token probe of every listed model then
     showed account eligibility.

  Each time the correction came from a file, a log or a real call. None came from recall.
- **The same failure, once more, in the analysis itself.** I asked for "the interval" as the headline without
  checking how it was computed. The percentile bootstrap degenerates on a 27/27 set, and the interval was too narrow
  until it was recomputed with score intervals (REPORT.md section 3, failure 5).

## Checking a drafted README against the files (2026-11-11)

A README drafted for publication was checked claim by claim against the
repository before being committed. Sixteen items failed across two rounds: five
numeric or count errors, and eleven statements that the files did not support.
Two are worth recording because of what kind of error they were:

- The draft claimed the three pre-registered questions all had power analyses
  computed before any result existed. The knob question had none; its ceiling was
  established after the sweep. A prediction that holds and an explanation found
  afterwards are not the same evidence, and the draft placed one as the other.
- The drafts attributed stale-value propagation to retrieval; draft 2 read
  "Retrieval largely determines whether a stale value is repeated". In this
  corpus "the correction was not retrieved" and "the correction was not
  marked" always co-occur, so retrieval cannot be isolated. This is the same
  confound flagged earlier in the audit, stated in the opposite direction.

Neither was caught by reading the draft. Both were caught by opening the files.

One of the sixteen did not come from the draft: the "3 of 15" figure for
SF11 originated in the checking report itself and was carried into the draft
from there. The count is kept at sixteen because that is how many items had
to be corrected before the file could be committed.

`reports/stale_fact_rule.md` still states that propagation on SF3, SF10 and
SF11 is "a retrieval failure, not a model failure". That file is the frozen
pre-registration and part of the hash set: it records what was believed
before any answer existed, and the audit later disproved it for SF3. It is
left unedited deliberately. Finding (c) carries the corrected reading.
