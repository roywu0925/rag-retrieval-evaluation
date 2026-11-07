"""Stale-fact runner. Implements mitigations/stale_prompt.json under reports/stale_fact_rule.md.

  .venv/bin/python scripts/run_stale.py --stability --arm us.anthropic.claude-haiku-4-5-20251001-v1:0
      baseline condition, one arm, run TWICE -> logs/stale_stability.jsonl (noise floor; never used as results)
  .venv/bin/python scripts/run_stale.py --main
      all conditions x arms -> logs/stale_answers.jsonl (refuses unless the freeze log matches; rule section 7)

Retrieval: base index titan-v2_cs512_ov100, top-5, exact cosine.
  exclude_context : CONTEXT.md chunks removed before ranking
  corrections_doc : base + corrections side index stacked, ranked together
  recency_*       : retrieval as baseline; label suffix + one instruction sentence in the prompt
Every call stops the run on the first exception (no retry).
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rag.embed import EmbeddingCache, embed  # noqa: E402
from rag.index import INDEX_DIR, Index, check_norms  # noqa: E402
from rag.sections import REGISTRY  # noqa: E402
from rag.stale_classify import BUCKET, classify, load  # noqa: E402

K = 5
BASE = INDEX_DIR / "titan-v2_cs512_ov100"
CORR = INDEX_DIR / "corrections_titan-v2_cs512_ov100"
PROMPT = ROOT / "mitigations/stale_prompt.json"
RECENCY = ROOT / "mitigations/recency_metadata.json"
RULE = ROOT / "reports/stale_fact_rule.md"
FACTS = ROOT / "eval/stale_facts.json"
PRICES = {"us.anthropic.claude-haiku-4-5-20251001-v1:0": (1.10, 5.50),
          "us.anthropic.claude-sonnet-4-6": (3.30, 16.50),
          "us.anthropic.claude-opus-4-6-v1": (5.50, 27.50)}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------- retrieval class (rule section 3)
def chunk_lines(c):
    """1-based file line numbers covered by a corpus chunk (body lines located inside the section)."""
    sec = REGISTRY[(c["file"], c["section"])]
    body = c["text"].split("\n", 1)[1].split("\n") if "\n" in c["text"] else []
    body = [l for l in body]
    for i in range(len(sec.lines)):
        if sec.lines[i:i + len(body)] == body:
            return set(range(sec.start_line + i, sec.start_line + i + len(body)))
    return set(range(sec.start_line, sec.end_line + 1))  # over-long-line splits: fall back to the section


def site_set(sites):
    out = {}
    for s in sites:
        m = re.match(r"(\S+\.md):(\d+)(?:-(\d+))?", s)
        if m:
            out.setdefault(m.group(1), set()).update(range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1))
    return out


def retrieval_class(chunks, fact):
    old, cur = site_set(fact["old_sites"]), site_set(fact["current_sites"])
    got_old = got_cur = False
    for c in chunks:
        if c["file"] == "CORRECTIONS.md":
            continue
        ls = chunk_lines(c)
        got_old |= bool(ls & old.get(c["file"], set()))
        got_cur |= bool(ls & cur.get(c["file"], set()))
    return {(True, False): "old-only", (False, True): "current-only", (True, True): "both",
            (False, False): "neither"}[(got_old, got_cur)]


# ---------- prompt
def excerpt(c, recency):
    if not recency or c["file"] not in recency:
        return c["text"]
    first, rest = c["text"].split("\n", 1)
    return first[:-1] + f" | last updated {recency[c['file']]}]\n" + rest


def build_prompt(P, question, chunks, recency):
    ex = "\n\n".join(excerpt(c, recency) for c in chunks)
    return P["template"].format(excerpts=ex, question=question,
                                recency_sentence=P["recency_sentence"] if recency else "")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--stability", action="store_true")
    g.add_argument("--main", action="store_true")
    ap.add_argument("--arm")
    a = ap.parse_args()

    pats, pat_sha = load()
    P = json.loads(PROMPT.read_text())
    facts = {f["id"]: f for f in json.loads(FACTS.read_text())}
    rec_meta = json.loads(RECENCY.read_text())
    s2_drop = pats["sensitivity_drop_markers"]["S2_without_original"]

    if a.stability:
        out, reps, conds, arms = ROOT / "logs/stale_stability.jsonl", 2, ["baseline"], [a.arm]
        assert a.arm in PRICES, a.arm
    else:
        out, reps = ROOT / "logs/stale_answers.jsonl", 1
        conds, arms = list(P["design"]["conditions"]), P["design"]["arms"]
        log = RULE.read_text()
        frozen = re.findall(r"`([^`]+)` sha256 ([0-9a-f]{64})", log.split("Freeze log:")[1])
        if not frozen:
            raise SystemExit("freeze log is empty; refusing to run (rule section 7)")
        for rel, h in frozen:
            if rel == "reports/stale_fact_rule.md":  # holds the log itself: hash the body above "Freeze log:"
                now = hashlib.sha256(log.split("Freeze log:")[0].encode()).hexdigest()
            else:
                now = sha(ROOT / rel)
            if now != h:
                raise SystemExit(f"{rel} changed since freeze; refusing to run")
    if out.exists():
        raise SystemExit(f"{out} exists; refusing to overwrite")

    base, corr = Index(BASE), Index(CORR)
    qids = list(pats["facts"])
    Q = embed([pats["facts"][q]["question"] for q in qids], model="titan-v2", input_type="query",
              cache=EmbeddingCache())
    check_norms(Q, "stale queries")

    import boto3
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    cost = 0.0
    for rep in range(reps):
        for arm in arms:
            for cond in conds:
                for qi, fid in enumerate(qids):
                    q = Q[qi]
                    if cond == "exclude_context":
                        s = base.M @ q
                        s[[i for i, c in enumerate(base.chunks) if c["file"] == "CONTEXT.md"]] = -np.inf
                        order = np.argsort(-s, kind="stable")[:K]
                        chunks = [base.chunks[i] for i in order]
                    elif cond == "corrections_doc":
                        allc = base.chunks + corr.chunks
                        s = np.concatenate([base.M, corr.M]) @ q
                        chunks = [allc[i] for i in np.argsort(-s, kind="stable")[:K]]
                    else:
                        idx, _ = base.search(q[None, :], K)
                        chunks = [base.chunks[i] for i in idx[0]]
                    recency = None
                    if cond.startswith("recency"):
                        recency = rec_meta[cond]["values"]
                    prompt = build_prompt(P, pats["facts"][fid]["question"], chunks, recency)
                    t0 = time.time()
                    try:
                        r = client.converse(modelId=arm, messages=[{"role": "user", "content": [{"text": prompt}]}],
                                            inferenceConfig=P["inference_config"])
                    except Exception as e:
                        raise SystemExit(f"STOPPED at rep {rep} {arm} {cond} {fid}: {type(e).__name__}: {e}")
                    ms = round(1000 * (time.time() - t0))
                    ans = "".join(b.get("text", "") for b in r["output"]["message"]["content"])
                    body = ans.split("Sources:")[0]
                    u = r["usage"]
                    pin, pout = PRICES[arm]
                    cost += u["inputTokens"] * pin / 1e6 + u["outputTokens"] * pout / 1e6
                    cls = classify(body, fid, pats)
                    rec = {"rep": rep, "fact": fid, "condition": cond, "arm": arm,
                           "retrieved": [c["chunk_id"] for c in chunks],
                           "corrections_reached": any(c["file"] == "CORRECTIONS.md" for c in chunks),
                           "retrieval_class": None if fid == "X1" else retrieval_class(chunks, facts[fid]),
                           "answer": ans, "class": cls,
                           "bucket": BUCKET.get(cls, cls),
                           "S1_bucket": "neither" if cls == "MIXED" else BUCKET.get(cls, cls),
                           "S2_class": classify(body, fid, pats, s2_drop),
                           "usage": {"in": u["inputTokens"], "out": u["outputTokens"]}, "latency_ms": ms,
                           "stop_reason": r.get("stopReason"), "patterns_sha256": pat_sha,
                           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
                    with open(out, "a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    print(f"rep{rep} {arm.split('.')[-1][:22]:22s} {cond:16s} {fid:5s} {cls:15s} "
                          f"{rec['retrieval_class']}  in={u['inputTokens']} out={u['outputTokens']}")
    print(f"cost ${cost:.4f}")


if __name__ == "__main__":
    main()
