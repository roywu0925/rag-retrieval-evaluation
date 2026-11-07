"""Rank-based power for Tier A (matched, n_a=28) vs Tier B (n_b=13). Pre-registration; no data.

Assumed generative model (no data exists, so this is an ASSUMPTION, varied for sensitivity):
  log(rank) ~ Normal(mu, sigma);  rank = clip(ceil(exp(.)), 1, N_CHUNKS)
  Tier A: mu chosen so that P(rank <= 5) = pA.   Tier B: mu + delta (worse).
For each delta: power of
  fisher_r5     : Fisher exact on recall@5                      (reference, = scripts/power.py)
  mwu_censored  : Mann-Whitney on rank censored at k=5 (ties at 6). IDENTICAL to Mann-Whitney on
                  reciprocal rank (monotone transform, same ties), so it is reported once.
  perm_mrr      : permutation test on the difference in MRR (means of 1/rank, 0 beyond k)
  mwu_full      : Mann-Whitney on the UNCENSORED rank among all chunks (exact retrieval ranks every chunk)
MDE = smallest delta reaching 80% power. Each MDE is reported as the TRUE recall@5 gap and TRUE MRR@5 gap it
corresponds to, so all tests share common units. Two-sided, alpha 0.05. Questions treated as independent.

  .venv/bin/python scripts/power_rank.py
"""
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import mannwhitneyu, norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from power import fisher_p  # noqa: E402

N_A, N_B, K, N_CHUNKS, ALPHA = 28, 13, 5, 100, 0.05
REPS, PERM = 1500, 400
rng = np.random.default_rng(0)


def draw(mu, sigma, n):
    return np.clip(np.ceil(np.exp(rng.normal(mu, sigma, n))), 1, N_CHUNKS).astype(int)


def mu_for(pa, sigma):  # P(ceil(exp(X)) <= 5) = P(X <= ln 5)
    return np.log(K) - sigma * norm.ppf(pa)


def rr(r):
    return np.where(r <= K, 1.0 / r, 0.0)


def true_stats(mu, sigma, n=400_000):
    r = draw(mu, sigma, n)
    return float(np.mean(r <= K)), float(np.mean(rr(r)))


def perm_p(x, y):
    obs = abs(x.mean() - y.mean())
    z = np.concatenate([x, y])
    idx = np.argsort(rng.random((PERM, len(z))), axis=1)
    Z = z[idx]
    d = np.abs(Z[:, :len(x)].mean(1) - Z[:, len(x):].mean(1))
    return (np.sum(d >= obs - 1e-12) + 1) / (PERM + 1)


def mwu_p(x, y):
    if np.all(x == x[0]) and np.all(y == x[0]):
        return 1.0
    return mannwhitneyu(x, y, alternative="two-sided", method="asymptotic").pvalue


def powers(pa, sigma, delta):
    mu = mu_for(pa, sigma)
    out = {"fisher_r5": 0, "mwu_censored": 0, "perm_mrr": 0, "mwu_full": 0}
    for _ in range(REPS):
        a, b = draw(mu, sigma, N_A), draw(mu + delta, sigma, N_B)
        out["fisher_r5"] += fisher_p(int((a <= K).sum()), N_A, int((b <= K).sum()), N_B) < ALPHA
        ca, cb = np.minimum(a, K + 1), np.minimum(b, K + 1)
        out["mwu_censored"] += mwu_p(ca, cb) < ALPHA
        out["perm_mrr"] += perm_p(rr(a), rr(b)) < ALPHA
        out["mwu_full"] += mwu_p(a, b) < ALPHA
    return {k: v / REPS for k, v in out.items()}


def main():
    deltas = np.round(np.arange(0.25, 4.01, 0.25), 2)
    for sigma in (1.0, 1.5):
        print(f"\n=== sigma={sigma} (rank spread assumption)   N_A={N_A} N_B={N_B}")
        print(" Tier A r@5 | test          | MDE @80%: true recall@5 gap | true MRR@5 gap")
        for pa in (0.6, 0.7, 0.8, 0.9):
            mu = mu_for(pa, sigma)
            r5a, mrra = true_stats(mu, sigma)
            found = {}
            for d in deltas:
                p = powers(pa, sigma, d)
                for t, v in p.items():
                    if t not in found and v >= 0.80:
                        r5b, mrrb = true_stats(mu + d, sigma)
                        found[t] = (r5a - r5b, mrra - mrrb)
                if len(found) == 4:
                    break
            for t in ("fisher_r5", "mwu_censored", "perm_mrr", "mwu_full"):
                g = found.get(t)
                s = f"{100 * g[0]:5.0f} pts            | {g[1]:.2f}" if g else "   not reached"
                print(f"   {pa:.1f}      | {t:13s} | {s}")
            print(f"            (Tier A true MRR@5 = {mrra:.2f})")


if __name__ == "__main__":
    main()
