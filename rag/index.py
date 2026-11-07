"""Exact cosine retrieval in numpy.

Both models return unit-norm vectors, so cosine == dot product and retrieval
is one matmul. That shortcut is only valid if the norms really are 1, so
check_norms() runs on every index build, index load and query batch, and
raises instead of silently mis-ranking.
"""
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from rag.chunker import chunk_corpus, measured_overlap
from rag.embed import EmbeddingCache, embed
from rag.sections import REGISTRY

INDEX_DIR = Path(__file__).resolve().parent.parent / "indexes"
NORM_TOL = 1e-3


def check_norms(M: np.ndarray, what: str) -> None:
    n = np.linalg.norm(M, axis=1)
    bad = np.where(np.abs(n - 1.0) > NORM_TOL)[0]
    if len(bad):
        raise ValueError(f"{what}: {len(bad)}/{len(n)} vectors not unit-norm within {NORM_TOL} "
                         f"(min {n.min():.6f}, max {n.max():.6f}). Normalise explicitly or fix the "
                         "adapter; a raw dot product would give wrong rankings.")


def index_name(model: str, config: Dict, tag: str = "") -> str:
    # overlap in per-mille, exact for the plan's values (0.095 -> ov095). Rounding to whole
    # percent once mapped 0.095 and 0.10 to the same name and overwrote an index.
    pm = config["overlap_pct"] * 1000
    if abs(pm - round(pm)) > 1e-9:
        raise ValueError(f"overlap_pct {config['overlap_pct']} not representable in per-mille")
    return f"{model}_cs{config['chunk_size']}_ov{int(round(pm)):03d}{tag}"


def build_index(model: str, config: Dict, tag: str = "", chunks: List[Dict] = None,
                dry_run: bool = False) -> Path:
    chunks = chunks if chunks is not None else chunk_corpus(config)
    for c in chunks:  # hit-rule metadata must survive into the index
        assert (c["file"], c["section"]) in REGISTRY
    M = embed([c["text"] for c in chunks], model=model, input_type="document",
              cache=EmbeddingCache(), dry_run=dry_run)
    check_norms(M, f"index {model}")
    out = INDEX_DIR / index_name(model, config, tag)
    if (out / "meta.json").exists():  # never overwrite an index built from a different config
        old = json.loads((out / "meta.json").read_text())
        if old["config"] != config or old["model"] != model:
            raise RuntimeError(f"{out.name} exists with config {old['config']}; refusing to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "vectors.npy", M)
    with open(out / "chunks.jsonl", "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    (out / "meta.json").write_text(json.dumps({
        "model": model, "config": config, "tag": tag, "n_chunks": len(chunks),
        "dim": int(M.shape[1]),
        "overlap_measured": measured_overlap(chunks, config["chunk_size"])}))
    return out


class Index:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.meta = json.loads((self.path / "meta.json").read_text())
        self.M = np.load(self.path / "vectors.npy")
        self.chunks = [json.loads(l) for l in (self.path / "chunks.jsonl").read_text().splitlines()]
        assert len(self.chunks) == self.M.shape[0]
        check_norms(self.M, f"load {self.path.name}")

    def search(self, Q: np.ndarray, k: int):
        """Q: [nq, d] unit-norm query vectors. Returns (indices [nq,k], scores [nq,k])."""
        check_norms(Q, "queries")
        S = Q @ self.M.T
        idx = np.argsort(-S, axis=1, kind="stable")[:, :k]
        return idx, np.take_along_axis(S, idx, axis=1)
