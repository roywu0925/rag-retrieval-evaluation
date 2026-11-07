"""Type M (exaggeration) check for the pre-registered A/B headline: (3) Tier A on Tier B sections, n = 27, vs (2) Tier B, n = 13.
Assumption: generated questions sit near ceiling (true recall 0.97; observed 27/27). For each plausible TRUE gap,
simulate 40,000 studies and report power (Fisher exact p < 0.05) and the mean observed gap among the significant
ones. Written AFTER the result (2026-11-06), to quantify how a significant result from this design is inflated; it
changes no pre-registered number.

  .venv/bin/python scripts/retrodesign_ab.py
"""
from functools import lru_cache

import numpy as np
from scipy.stats import fisher_exact

rng = np.random.default_rng(0)
nA, nB, pA = 27, 13, 0.97


@lru_cache(None)
def sig(a, b):
    return fisher_exact([[a, nA - a], [b, nB - b]])[1] < 0.05


print("true gap | power | mean observed gap among significant results | exaggeration")
for gap in (0.05, 0.10, 0.15, 0.20, 0.30):
    a, b = rng.binomial(nA, pA, 40000), rng.binomial(nB, pA - gap, 40000)
    s = np.array([sig(x, y) for x, y in zip(a, b)])
    obs = a / nA - b / nB
    print(f"  {100 * gap:4.0f}   | {s.mean():.2f}  | {100 * obs[s].mean():5.1f} pts | {obs[s].mean() / gap:.1f}x")
