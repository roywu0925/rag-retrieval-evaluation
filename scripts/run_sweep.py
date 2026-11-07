"""OFAT sweep runner (rag/sweep_plan.py). One config per invocation.

  .venv/bin/python scripts/run_sweep.py --run base            # retrieval for all pools + answer calls
  .venv/bin/python scripts/run_sweep.py --project base        # project the other configs' cost from base (no calls)

Questions
  answered (Haiku 4.5): Tier A main pool (eval/tier_a.jsonl) + Tier B (eval/tier_b.jsonl)
  retrieval only:       Tier A top-up and paired pools (they feed analyses (3) and the paired comparison)
Retrieval metrics (free; exact cosine over the full ranking)
  rank        rank at which the question is satisfied (multi_section strict = every required_all group covered;
              lenient = any gold section); None for NO_GOLD
  hit@1/3/5/k, rr@k (reciprocal rank, 0 beyond k)
  chance@k    exact probability that k chunks drawn uniformly at random satisfy the question (inclusion-exclusion
              over required groups), which is the random-retrieval baseline column
Answer metrics, DEFINED HERE BEFORE ANY SWEEP ANSWER EXISTS
  cited       [file > section] labels parsed from the answer's "Sources:" line
  cite_gold   answerable: some cited label is a gold / also_acceptable section (multi_section strict: every group
              cited; lenient: any gold)
  cite_valid  every cited label is the label of a chunk that was actually retrieved (no fabricated citation)
  abstained   the answer matches an abstention phrase from eval/stale_patterns.json (for NO_GOLD questions this
              is the score; it is measured under the prompt's explicit abstention instruction, so it is an upper bound)
Prompt: mitigations/stale_prompt.json template, no recency sentence. Model us.anthropic.claude-haiku-4-5,
temperature 0. Stops on the first exception (no retry).
"""
import argparse
import json
import re
import sys
import time
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rag.embed import EmbeddingCache, embed  # noqa: E402
from rag.index import INDEX_DIR, Index, check_norms, index_name  # noqa: E402
from rag.sections import NO_GOLD, _groups, category, gold_ids, load_eval_set  # noqa: E402
from rag.sweep_plan import RUNS, config_for  # noqa: E402
from rag.tokens import ntok  # noqa: E402

ARM = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
PIN, POUT = 1.10, 5.50
OUTDIR = ROOT / "logs/sweep"
POOLS = {"A_main": ("eval/tier_a.jsonl", True), "B": ("eval/tier_b.jsonl", True),
         "A_topup": ("eval/tier_a_topup.jsonl", False), "A_paired": ("eval/tier_a_paired.jsonl", False)}
P = json.loads((ROOT / "mitigations/stale_prompt.json").read_text())
ABST = json.loads((ROOT / "eval/stale_patterns.json").read_text())["abstention_phrases"]
LABEL = re.compile(r"\[([^\[\]>|]+?)\s*>\s*([^\[\]|]+?)\s*(?:\|[^\]]*)?\]")


def qid(pool, i, q):
    return q.get("id") or f"{pool}-{i:02d}"


def need_groups(q, rule):
    if category(q) == "multi_section" and rule == "strict":
        return _groups(q)
    return [gold_ids(q)]


def satisfied_rank(order, chunks, groups):
    """1-based rank at which every group has at least one chunk; None if never."""
    left = [set(g) for g in groups]
    for r, i in enumerate(order, 1):
        sid = (chunks[i]["file"], chunks[i]["section"])
        left = [g for g in left if sid not in g]
        if not left:
            return r
    return None


def chance(chunks, groups, k):
    """P(k uniform random chunks cover every group), exact inclusion-exclusion."""
    N = len(chunks)
    sizes = [sum((c["file"], c["section"]) in g for c in chunks) for g in groups]
    tot = 0.0
    for m in range(len(groups) + 1):
        for S in combinations(range(len(groups)), m):
            union = set().union(*[groups[j] for j in S]) if S else set()
            n_s = sum((c["file"], c["section"]) in union for c in chunks)
            tot += (-1) ** m * comb(N - n_s, k) / comb(N, k)
    return tot if all(sizes) else 0.0


def load_pools():
    out = []
    for pool, (path, answered) in POOLS.items():
        p = ROOT / path
        if not p.exists():
            continue
        for i, q in enumerate(load_eval_set(p)):
            out.append((pool, qid(pool, i, q), q, answered))
    return out


def context_tokens(chunks, idx):
    return sum(ntok(chunks[i]["text"]) for i in idx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--project")
    a = ap.parse_args()
    items = load_pools()
    Q = embed([q["question"] for _, _, q, _ in items], model="titan-v2", input_type="query", cache=EmbeddingCache())
    check_norms(Q, "sweep queries")

    if a.project:  # cost projection from a measured config: no calls
        meas = [json.loads(l) for l in open(OUTDIR / f"{a.project}.jsonl") if json.loads(l).get("answer") is not None]
        base_ctx = np.mean([m["context_tokens_proxy"] for m in meas])
        ratio = np.mean([m["usage"]["in"] for m in meas]) / base_ctx       # bedrock input tokens per proxy ctx token
        out_mean = np.mean([m["usage"]["out"] for m in meas])
        print(f"measured {a.project}: {len(meas)} calls, input {np.mean([m['usage']['in'] for m in meas]):.0f}/call, "
              f"output {out_mean:.0f}/call, bedrock/proxy ratio {ratio:.3f}")
        tot = 0.0
        for rid, _, _ in RUNS:
            cfg, _ = config_for(rid)
            ix = Index(INDEX_DIR / index_name(cfg["model"], cfg))
            ctx = [context_tokens(ix.chunks, ix.search(Q[j][None, :], cfg["k"])[0][0])
                   for j, (_, _, _, ans) in enumerate(items) if ans]
            cin = ratio * np.mean(ctx)
            c = len(ctx) * (cin * PIN + out_mean * POUT) / 1e6
            tot += c
            print(f"  {rid:15s} k={cfg['k']:2d} cs={cfg['chunk_size']:4d}  ~{cin:6.0f} in/call  {len(ctx)} calls  ${c:.4f}")
        print(f"sweep total (all {len(RUNS)} configs, incl. the measured one): ${tot:.4f}")
        return

    cfg, axis = config_for(a.run)
    ix = Index(INDEX_DIR / index_name(cfg["model"], cfg))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"{a.run}.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists; refusing to overwrite")
    import boto3
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    cost, k = 0.0, cfg["k"]
    for j, (pool, i_d, q, answered) in enumerate(items):
        S = ix.M @ Q[j]
        order = np.argsort(-S, kind="stable")
        rec = {"run": a.run, "axis": axis, "config": cfg, "pool": pool, "id": i_d, "category": category(q),
               "lang": q.get("lang") or ("zh" if q.get("tier") == "B" else "en"), "pair_of": q.get("pair_of"),
               "variant": q.get("variant") or ("R" if q.get("tier") == "B" else None),
               "retrieved": [ix.chunks[i]["chunk_id"] for i in order[:k]], "n_chunks": len(ix.chunks)}
        if category(q) not in NO_GOLD:
            for rule in ("strict", "lenient"):
                g = need_groups(q, rule)
                r = satisfied_rank(order, ix.chunks, g)
                rec[rule] = {"rank": r, **{f"hit@{n}": bool(r and r <= n) for n in (1, 3, 5, k)},
                             f"rr@{k}": (1.0 / r if r and r <= k else 0.0),
                             f"chance@{k}": chance(ix.chunks, g, k), "chance@5": chance(ix.chunks, g, 5)}
        rec["context_tokens_proxy"] = context_tokens(ix.chunks, order[:k])
        rec["answer"] = None
        if answered:
            chunks = [ix.chunks[i] for i in order[:k]]
            prompt = P["template"].format(excerpts="\n\n".join(c["text"] for c in chunks), question=q["question"],
                                          recency_sentence="")
            t0 = time.time()
            try:
                resp = client.converse(modelId=ARM, messages=[{"role": "user", "content": [{"text": prompt}]}],
                                       inferenceConfig=P["inference_config"])
            except Exception as e:
                raise SystemExit(f"STOPPED at {a.run} {i_d}: {type(e).__name__}: {e}")
            ans = "".join(b.get("text", "") for b in resp["output"]["message"]["content"])
            u = resp["usage"]
            cost += u["inputTokens"] * PIN / 1e6 + u["outputTokens"] * POUT / 1e6
            src = ans.split("Sources:", 1)[1] if "Sources:" in ans else ""
            cited = {(f.strip(), s.strip()) for f, s in LABEL.findall(src)}
            got = {(c["file"], c["section"]) for c in chunks}
            rec.update(answer=ans, latency_ms=round(1000 * (time.time() - t0)),
                       usage={"in": u["inputTokens"], "out": u["outputTokens"]}, stop_reason=resp.get("stopReason"),
                       cited=sorted(cited), cite_valid=bool(cited) and cited <= got,
                       abstained=any(re.search(p, ans.split("Sources:")[0].lower()) for p in ABST))
            if category(q) not in NO_GOLD:
                rec["cite_gold"] = {rule: all(cited & g for g in need_groups(q, rule)) for rule in ("strict", "lenient")}
        with open(out, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{a.run}: {len(items)} questions, cost ${cost:.4f}")


if __name__ == "__main__":
    main()
