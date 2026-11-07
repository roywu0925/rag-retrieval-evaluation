"""Empirical checks on Cohere Embed v4 before any index is built with it.

  --prepare                         write probe text files (free, no API)
  --model M <textfile>              embed the file twice (search_document, search_query); 2 calls
  --model M --bad-input-type        send input_type="search_documnet" on a short text; 1 call

Each call uses rag.embed.BODY_BUILDERS[M], the exact body the index build sends.

What each run reports and why:
  status / error      did the API accept this length at all
  billed tokens       x-amzn-bedrock-input-token-count. If the API truncated silently,
                      billed tokens stop growing with length: compare tokens/char across files
  dim, norm           index build requires unit norm within 1e-3
  cos(doc, query)     same text under both input_types. ~1.0 means input_type is ignored
                      (no asymmetric embedding); clearly < 1 means it changes the vector
Results append to probe/results.jsonl.
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rag.embed import BODY_BUILDERS, MODELS, REGION, ROUTING  # noqa: E402

PROBE = ROOT / "probe"


def prepare():
    from rag.chunker import BASELINE, chunk_corpus
    from rag.sections import REGISTRY
    PROBE.mkdir(exist_ok=True)
    longest = max(chunk_corpus(BASELINE), key=lambda c: len(c["text"]))
    (PROBE / "v4_2303.txt").write_text(longest["text"])
    # ~6,000 chars of contiguous real text from the largest section, cut on a line boundary
    sec = max(REGISTRY.values(), key=lambda s: len(s.text))
    out, n = [f"[{sec.file} > {sec.path}]"], 0
    for l in sec.lines[1:]:
        if n + len(l) + 1 > 6000:
            break
        out.append(l)
        n += len(l) + 1
    (PROBE / "v4_6000.txt").write_text("\n".join(out))
    # v3: longest chunk of the 256-token config, the regime v3 runs in under plan D
    l256 = max(chunk_corpus({"chunk_size": 256, "overlap_pct": 0.10}), key=lambda c: len(c["text"]))
    (PROBE / "v3_1263.txt").write_text(l256["text"])
    for f in ("v4_2303.txt", "v4_6000.txt", "v3_1263.txt"):
        print(f"wrote probe/{f}: {len((PROBE / f).read_text())} chars")


def call(client, model, text, input_type_raw):  # one invoke, never retried
    body = BODY_BUILDERS[model]([text], "document")
    body["input_type"] = input_type_raw  # raw string so --bad-input-type can bypass the mapping
    t0 = time.time()
    try:
        r = client.invoke_model(modelId=MODELS[model][0], body=json.dumps(body),
                                contentType="application/json", accept="application/json")
    except Exception as e:  # report, never retry
        return {"input_type": input_type_raw, "ok": False, "error": f"{type(e).__name__}: {e}"}
    hdr = r["ResponseMetadata"]["HTTPHeaders"]
    resp = json.loads(r["body"].read())
    embs = resp["embeddings"]["float"] if isinstance(resp["embeddings"], dict) else resp["embeddings"]
    raw = embs[0]
    v = np.asarray(raw, dtype=np.float64)
    echoed = resp.get("texts") or [None]
    return {"input_type": input_type_raw, "ok": True, "latency_ms": round(1000 * (time.time() - t0)),
            "requested_embedding_types": body.get("embedding_types", "(not sent; v3 default float)"),
            "response_embedding_keys": sorted(resp["embeddings"]) if isinstance(resp["embeddings"], dict) else "list",
            "raw_json_value_type": type(raw[0]).__name__,
            "array_dtype": str(v.dtype),
            "chars_sent": len(text), "chars_echoed": None if echoed[0] is None else len(echoed[0]),
            "raw": raw,
            "billed_tokens": int(hdr.get("x-amzn-bedrock-input-token-count", -1)),
            "n_vectors": len(embs), "dim": len(v), "norm": float(np.linalg.norm(v)),
            "resp_keys": sorted(resp), "vec": v,
            "region_header": {k: v2 for k, v2 in hdr.items() if "region" in k.lower()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textfile", nargs="?")
    ap.add_argument("--model", choices=sorted(BODY_BUILDERS))
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--bad-input-type", action="store_true")
    a = ap.parse_args()
    if a.prepare:
        return prepare()

    if not a.model:
        ap.error("--model is required for API calls")
    import boto3
    client = boto3.client("bedrock-runtime", region_name=REGION)
    if a.bad_input_type:
        runs, label = [call(client, a.model, "probe text for validation", "search_documnet")], "bad-input-type"
    else:
        a_file = a.textfile
        text = Path(a.textfile).read_text()
        label = f"{Path(a.textfile).name} ({len(text)} chars)"
        runs = [call(client, a.model, text, "search_document"), call(client, a.model, text, "search_query")]

    print(f"== {MODELS[a.model][0]}  [{ROUTING[a.model]}]  {label}")
    for r in runs:
        if not r["ok"]:
            print(f"  {r['input_type']:16s} FAILED  {r['error'][:300]}")
            continue
        print(f"  {r['input_type']:16s} ok  billed_tokens={r['billed_tokens']}  dim={r['dim']}  "
              f"norm={r['norm']:.6f}  latency={r['latency_ms']}ms ({ROUTING[a.model]})")
        print(f"  {'':16s} requested={r['requested_embedding_types']} returned={r['response_embedding_keys']} "
              f"json_type={r['raw_json_value_type']} dtype={r['array_dtype']} "
              f"chars sent/echoed={r['chars_sent']}/{r['chars_echoed']} region_hdr={r['region_header']}")
    if len(runs) == 2 and all(r["ok"] for r in runs):
        # Two independent paths. numpy 2.0.x + macOS Accelerate emits spurious FP
        # warnings in matmul, so the BLAS path is cross-checked by exact summation.
        a, b = runs[0]["raw"], runs[1]["raw"]
        cos_exact = math.fsum(x * y for x, y in zip(a, b)) / math.sqrt(
            math.fsum(x * x for x in a) * math.fsum(y * y for y in b))
        with np.errstate(all="ignore"):
            cos_blas = float(np.dot(runs[0]["vec"], runs[1]["vec"]) /
                             (np.linalg.norm(runs[0]["vec"]) * np.linalg.norm(runs[1]["vec"])))
        print(f"  cos(search_document, search_query) exact fsum = {cos_exact:.6f}   "
              f"numpy dot = {cos_blas:.6f}   |diff| = {abs(cos_exact - cos_blas):.1e}")
        np.save(PROBE / f"vecs_{a.model}_{Path(a_file).stem}.npy", np.vstack([runs[0]["vec"], runs[1]["vec"]]))
        print(f"  chars per billed token = {len(text) / max(runs[0]['billed_tokens'], 1):.2f}")
    PROBE.mkdir(exist_ok=True)
    with open(PROBE / "results.jsonl", "a") as f:
        for r in runs:
            r = {k: v for k, v in r.items() if k not in ("vec", "raw")}
            f.write(json.dumps({"model": a.model, "label": label, **r}) + "\n")


if __name__ == "__main__":
    main()
