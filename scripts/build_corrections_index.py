"""Build the corrections-doc side index for the stale-fact 'corrections_doc' condition.
mitigations/CORRECTIONS.md is chunked by the SAME chunker at the base config (512 / 10%) and embedded with Titan v2
(document). Stored separately: it is not a corpus file, so it is outside the REGISTRY and the hit rule. At query time
it is stacked onto the base index, and retrieval decides whether it is reached.

  .venv/bin/python scripts/build_corrections_index.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rag.chunker import BASELINE, chunk_section  # noqa: E402
from rag.embed import EmbeddingCache, embed  # noqa: E402
from rag.index import INDEX_DIR, check_norms, index_name  # noqa: E402
from rag.sections import parse_file  # noqa: E402

SRC = ROOT / "mitigations"
OUT = INDEX_DIR / ("corrections_" + index_name("titan-v2", BASELINE))


def main():
    if (OUT / "meta.json").exists():
        raise SystemExit(f"{OUT} exists; refusing to overwrite")
    chunks = []
    for sec in parse_file("CORRECTIONS.md", corpus=SRC):
        for c in chunk_section(sec, BASELINE["chunk_size"], BASELINE["overlap_pct"]):
            c["chunk_id"] = f"{c['file']}::{c['section']}::{c['idx_in_section']}"
            c["text_sha256"] = hashlib.sha256(c["text"].encode()).hexdigest()
            chunks.append(c)
    cache = EmbeddingCache()
    before = cache.billed_tokens("titan-v2")
    M = embed([c["text"] for c in chunks], model="titan-v2", input_type="document", cache=cache)
    check_norms(M, "corrections index")
    OUT.mkdir(parents=True)
    np.save(OUT / "vectors.npy", M)
    with open(OUT / "chunks.jsonl", "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    src_sha = hashlib.sha256((SRC / "CORRECTIONS.md").read_bytes()).hexdigest()
    (OUT / "meta.json").write_text(json.dumps({"model": "titan-v2", "config": BASELINE, "tag": "corrections",
                                               "n_chunks": len(chunks), "dim": int(M.shape[1]),
                                               "source_sha256": src_sha}))
    billed = cache.billed_tokens("titan-v2") - before
    print(f"{len(chunks)} chunks ({[c['tokens'] for c in chunks]} tok), billed {billed} tokens = ${billed * 0.02e-6:.6f}")


if __name__ == "__main__":
    main()
