"""What Tier A vs Tier B recall@5 gap can this design detect? (pre-registration; no data)

Two independent proportions: Tier A matched (n_a) vs Tier B (n_b), Fisher exact two-sided, alpha 0.05.
  (a) significance threshold: for each observed Tier A count, the smallest observed gap that reaches p < .05
  (b) MDE: smallest TRUE gap detected with 80% power (Monte Carlo, 4000 draws per point)
Treats questions as independent. Tier A top-up questions share sections, so the true power is somewhat LOWER.

  .venv/bin/python scripts/power.py
"""
from functools import lru_cache
from math import comb

import numpy as np

N_A, N_B, ALPHA, POWER = 28, 13, 0.05, 0.80


@lru_cache(maxsize=None)
def fisher_p(a, na, b, nb):
    """Two-sided Fisher exact p for successes a/na vs b/nb (sum of tables no more likely than observed)."""
    k, n = a + b, na + nb
    lo, hi = max(0, k - nb), min(k, na)
    probs = {x: comb(na, x) * comb(nb, k - x) / comb(n, k) for x in range(lo, hi + 1)}
    p_obs = probs[a]
    return min(1.0, sum(p for p in probs.values() if p <= p_obs * (1 + 1e-9)))


def threshold_gap(a, na=N_A, nb=N_B):
    """Smallest observed gap pA_hat - pB_hat (Tier B lower) that is significant, given a/na for Tier A."""
    for b in range(nb, -1, -1):
        if b / nb < a / na and fisher_p(a, na, b, nb) < ALPHA:
            return a / na - b / nb
    return None


def power(pa, pb, na=N_A, nb=N_B, reps=4000, rng=np.random.default_rng(0)):
    A, B = rng.binomial(na, pa, reps), rng.binomial(nb, pb, reps)
    return float(np.mean([fisher_p(int(x), na, int(y), nb) < ALPHA for x, y in zip(A, B)]))


def mde(pa, na=N_A, nb=N_B):
    for d in np.arange(0.01, pa + 1e-9, 0.01):
        if power(pa, pa - d, na, nb) >= POWER:
            return round(float(d), 2)
    return None


if __name__ == "__main__":
    for na in (14, 28):
        print(f"\n== Tier A matched n={na}  vs  Tier B n={N_B}")
        print(" Tier A recall@5 | (a) min observed gap for p<.05 | (b) true gap for 80% power")
        for pa in (0.6, 0.7, 0.8, 0.9, 1.0):
            a = round(pa * na)
            t = threshold_gap(a, na)
            m = mde(pa, na)
            print(f"   {pa:.1f} ({a}/{na})      | {('%.0f pts' % (100 * t)) if t else 'none':>8s}"
                  f"                     | {('%.0f pts' % (100 * m)) if m else '> pA'}")
