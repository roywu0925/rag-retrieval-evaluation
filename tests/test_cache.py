"""Cache-key behaviour with a fake adapter (no API calls).
Run:  .venv/bin/python tests/test_cache.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rag.embed as E  # noqa: E402
from rag.chunker import chunk_corpus  # noqa: E402

calls = []


def fake(client, texts, input_type):
    calls.extend((t, input_type) for t in texts)
    out = []
    for t in texts:
        v = np.random.default_rng(abs(hash((t, input_type))) % 2**32).standard_normal(8)
        out.append(((v / np.linalg.norm(v)).tolist(), 1))
    return out


def main():
    E.ADAPTERS["titan-v2"] = fake
    E._client = lambda: None
    with tempfile.TemporaryDirectory() as d:
        cache = E.EmbeddingCache(Path(d) / "c.sqlite")
        a = [c["text"] for c in chunk_corpus({"chunk_size": 512, "overlap_pct": 0.10})]
        b = [c["text"] for c in chunk_corpus({"chunk_size": 1024, "overlap_pct": 0.10})]
        Va = E.embed(a, model="titan-v2", input_type="document", cache=cache)
        n_a = len(calls)
        Vb = E.embed(b, model="titan-v2", input_type="document", cache=cache)
        shared = set(a) & set(b)
        assert n_a == len(set(a))
        assert len(calls) - n_a == len(set(b) - set(a)), "shared texts were re-embedded"
        # identical text -> identical vector regardless of which config produced it
        ia = {t: i for i, t in enumerate(a)}
        for j, t in enumerate(b):
            if t in shared:
                assert np.array_equal(Va[ia[t]], Vb[j])
        # in-call repeats embedded once
        before = len(calls)
        E.embed(["dup text x", "dup text x"], model="titan-v2", input_type="document", cache=cache)
        assert len(calls) - before == 1
        # document and query vectors never share a cache entry
        before = len(calls)
        E.embed(["dup text x"], model="titan-v2", input_type="query", cache=cache)
        assert len(calls) - before == 1 and calls[-1][1] == "query"
        # unknown input_type rejected at the key
        try:
            cache.key("titan-v2", "search_document", "x")
            raise AssertionError("bad input_type accepted")
        except ValueError:
            pass
    print(f"OK: {len(shared)} texts shared between 512 and 1024 configs, embedded once; "
          "doc/query separated; in-call repeats deduped")


if __name__ == "__main__":
    main()
