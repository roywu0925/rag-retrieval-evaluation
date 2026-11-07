"""Build one embedding index.

  .venv/bin/python scripts/build_index.py --model titan-v2              # baseline 512 / 10%
  .venv/bin/python scripts/build_index.py --model titan-v2 --dry-run    # stats + cost, no API calls
  .venv/bin/python scripts/build_index.py --model titan-v2 --chunk-size 256 --overlap 0.25
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.chunker import BASELINE, chunk_corpus, measured_overlap  # noqa: E402
from rag.embed import MAX_CHARS, MODELS, EmbeddingCache  # noqa: E402
from rag.index import build_index, index_name  # noqa: E402
from rag.sections import REGISTRY  # noqa: E402


def stats(chunks, model, config):
    tok = np.array([c["tokens"] for c in chunks])
    per_sec = {}
    for c in chunks:
        per_sec[(c["file"], c["section"])] = c["n_in_section"]
    biggest = max(REGISTRY.values(), key=lambda s: len(s.text))
    chars = np.array([len(c["text"]) for c in chunks])
    print(f"sections in registry      : {len(REGISTRY)}  (non-empty: {len(per_sec)})")
    print(f"total chunks              : {len(chunks)}")
    print(f"chunk tokens min/med/p90/max: {tok.min()} / {int(np.median(tok))} / "
          f"{int(np.percentile(tok, 90))} / {tok.max()}   (sum {tok.sum()})")
    whole = sum(c["is_whole_section"] for c in chunks)
    print(f"whole-section chunks      : {whole}   fragment chunks: {len(chunks) - whole}")
    print(f"sections -> exactly 1 chunk: {sum(v == 1 for v in per_sec.values())} of {len(per_sec)}")
    print(f"largest section           : {biggest.file} :: {biggest.path} -> "
          f"{per_sec[biggest.id]} chunks")
    lim = MAX_CHARS[model]
    print(f"chunk chars max           : {chars.max()}   {model} limit: "
          f"{'UNVERIFIED' if lim is None else lim}"
          + ("" if lim is None else f"   over limit: {(chars > lim).sum()}"))
    mo = measured_overlap(chunks, config["chunk_size"])
    print(f"overlap MEASURED          : {mo['pct']:.1f}% of chunk_size per continuation chunk "
          f"({mo['n_continuation']} of {mo['n_chunks']}); {mo['pct_all']:.1f}% of embedded tokens "
          f"are duplicates   [nominal {config['overlap_pct']:.0%}]")
    return int(tok.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--chunk-size", type=int, default=BASELINE["chunk_size"])
    ap.add_argument("--overlap", type=float, default=BASELINE["overlap_pct"])
    ap.add_argument("--dry-run", action="store_true", help="stats and cost estimate only")
    a = ap.parse_args()
    config = {"chunk_size": a.chunk_size, "overlap_pct": a.overlap}

    chunks = chunk_corpus(config)
    print(f"== {index_name(a.model, config)}")
    total_tok = stats(chunks, a.model, config)

    cache = EmbeddingCache()
    uncached, seen = [], set()
    for c in chunks:
        k = cache.key(a.model, "document", c["text"])[0]
        if k not in seen and cache.get(k) is None:
            uncached.append(c)
        seen.add(k)
    unc_tok = sum(c["tokens"] for c in uncached)
    price = MODELS[a.model][1]
    print(f"uncached chunks           : {len(uncached)}  (~{unc_tok} cl100k tokens)")
    print(f"estimated cost            : ${unc_tok * price / 1e6:.5f}  "
          f"(at ${price}/1M; full index ${total_tok * price / 1e6:.5f})")
    if a.dry_run:
        print("dry run: no API calls made")
        return

    before = cache.billed_tokens(a.model)
    out = build_index(a.model, config, chunks=chunks)
    billed = EmbeddingCache().billed_tokens(a.model) - before
    print(f"built {out}")
    print(f"billed tokens this run    : {billed}  -> ${billed * price / 1e6:.5f}")


if __name__ == "__main__":
    main()
