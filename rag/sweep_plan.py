"""OFAT sweep plan, written down before any results exist.

Baseline: titan-v2, chunk_size 512, nominal overlap 10% (measured 8.2%), top-k 5.
Overlap is reported as MEASURED (chunker.measured_overlap); nominal is a footnote.

INTERACTION CHECK (tests OFAT's no-interaction premise):
  For s in {256, 1024}, with recall@5 R(.):
    direct       = R(s, matched) - R(512, base)        # overlap held near 8.2-8.6%
    extrapolated = [R(s, nominal 10%) - R(512, base)] - slope * (ov(s, 10%) - ov(512, 10%))
      where slope = dR/d(overlap pt) from the 512 overlap axis (0 -> 8.2 segment;
      a 3-point linear fit is reported as a check).
  extrapolated == overlap-corrected chunk-size effect assuming no interaction.
  Report both side by side with the gap, in raw recall AND recall above random.
  Agreement -> the OFAT ranking reads at face value. A gap -> chunk size and overlap
  interact; the ranking depends on where the other knobs sit, and is reported as such.

  EVIDENCE STRENGTH (fixed before results):
    cs1024_matched differs from cs1024 in only 2 of 64 chunks (nominal 9.5% vs 10%), so it is
    NOT independent evidence; it is run anyway (prediction is not measurement) and reported
    with that framing.
    The interaction check therefore rests on ONE comparison, the 256 pair (98 of 181 chunks
    differ). "No interaction" there is one observation, not a demonstration that OFAT's
    no-interaction premise holds, and the write-up must say so.

MODEL AXIS: cut. Titan v2 only (see note under RUNS).
"""

BASE = {"model": "titan-v2", "chunk_size": 512, "overlap_pct": 0.10, "k": 5}

RUNS = [
    # (run id, axis, overrides on BASE)
    ("base",          "baseline",    {}),
    ("cs256",         "chunk_size",  {"chunk_size": 256}),
    ("cs1024",        "chunk_size",  {"chunk_size": 1024}),
    ("ov0",           "overlap",     {"overlap_pct": 0.0}),
    ("ov25",          "overlap",     {"overlap_pct": 0.25}),
    ("k3",            "top_k",       {"k": 3}),
    ("k10",           "top_k",       {"k": 10}),
    # matched-overlap runs: nominal chosen so measured overlap ~= 8.2% (512 baseline)
    ("cs256_matched",  "interaction", {"chunk_size": 256, "overlap_pct": 0.120}),   # measured 8.56%
    ("cs1024_matched", "interaction", {"chunk_size": 1024, "overlap_pct": 0.095}),  # measured 8.42%
]
# top-k runs reuse the baseline index (no extra embedding); 7 distinct indexes in total.
# Model axis CUT 2026-11-04 (Roy): a delta measured at 256 while every other axis sits at 512
# would weaken the knob ranking more than the extra knob adds. Titan v2 only.


def config_for(run_id):
    for rid, axis, ov in RUNS:
        if rid == run_id:
            return {**BASE, **ov}, axis
    raise KeyError(run_id)
