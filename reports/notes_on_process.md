# Notes on process

- **Checking beat remembering, three times.**
  1. In one instruction about the stale-fact write-up (2026-11-06), I made four claims that the record or the data
     did not support:
     - a **misattributed decision**: I said I had removed "week 1" as a marker against the assistant's advice,
       when the assistant had proposed it;
     - an **overstated statistical reading**: "performed at chance", on a stratum where kappa is degenerate;
     - a **confounded causal claim**: "the marker, not the model", when marker and retrieval coincide;
     - an **extrapolation without its interval**: "near zero where marked", which omitted 14 unaudited
       rule-PROPAGATED answers on marked facts and the 17% upper bound.

     All four were caught by checking against the files, not against memory.
  2. It is the same failure mode as the résumé numbers: assertions that felt right and had no source. Those
     included an 8.6x with no output behind it, an 11% that regenerates to 11.5%, a ~4,000 km that is ~3,500, and a
     $0.12/hr that is $0.115/hr in the price list.
  3. It is also the same failure mode as the assistant's own explanations of the Bedrock access failures. It first
     blamed the model agreement for the Cohere errors (operational_findings.md OF1, withdrawn to UNRESOLVED), then
     a missing per-model subscription for Sonnet 5.5 (OF3, corrected the same day). A 1-token probe of every
     listed model then showed account eligibility.

  Each time the correction came from a file, a log or a real call. None came from recall.
