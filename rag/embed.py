"""Per-model Bedrock embedding adapters with an on-disk cache.

input_type is a REQUIRED argument everywhere ("document" or "query"):
Cohere silently degrades if search_document / search_query are swapped,
so no default exists to get wrong. Titan ignores it, but it is still
part of the cache key, so a query vector is never served as a document.

Cache key = (MODEL_SPEC[model], input_type, sha256(text)).
A vector depends on the model and its request parameters, the input_type,
and the text, and nothing else. Chunk size and overlap decide WHICH texts
exist; they never change the vector of a given text, so they are
deliberately NOT in the key. A text produced by two configs is embedded
once. MODEL_SPEC includes every request parameter that changes the vector
(e.g. Titan dimensions/normalize). Change a parameter -> change the spec.
Billed input tokens come from the Bedrock response header and are stored,
so spend is auditable.
"""
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import List, Optional

import numpy as np

REGION = "us-west-2"
CACHE_DB = Path(__file__).resolve().parent.parent / "cache" / "embeddings.sqlite"

MODELS = {
    # key: (bedrock model id, USD per 1M input tokens, max texts per call)
    "titan-v2": ("amazon.titan-embed-text-v2:0", 0.02, 1),
    "cohere-v3": ("cohere.embed-english-v3", 0.10, 96),
    # v4 is INFERENCE_PROFILE-only in us-west-2 (no on-demand model id).
    "cohere-v4": ("us.cohere.embed-v4:0", 0.12, 96),
}
COHERE_INPUT_TYPE = {"document": "search_document", "query": "search_query"}
TITAN_DIM = 1024

# Cache identity of each model: the model id plus every request parameter that
# changes the returned vector. Must be kept in step with the adapters below.
MODEL_SPEC = {
    "titan-v2": f"amazon.titan-embed-text-v2:0|dimensions={TITAN_DIM}|normalize=true",
    "cohere-v3": "cohere.embed-english-v3|truncate=NONE",
    "cohere-v4": "us.cohere.embed-v4:0|output_dimension=1024|embedding_types=float|truncate=NONE",
}

# Latency comparability. A cross-region profile can route to another region, so
# its latency is reported in its own row and excluded from any between-model
# latency comparison. Recall comparisons are unaffected.
ROUTING = {
    "titan-v2": "in-region",
    "cohere-v3": "in-region",
    "cohere-v4": "cross-region-profile",
}

# Per-text character limits. None = not yet verified empirically; embed()
# refuses to run a model whose limit is unverified, so no index is built on
# a documented figure. Set from scripts/probe_cohere_v4.py results.
MAX_CHARS = {
    "titan-v2": 50_000,   # 8k-token model limit; corpus max chunk is 4,210 chars
    "cohere-v3": 2048,    # Bedrock per-text limit; the 0.999951 norm was measured on this model
    "cohere-v4": None,    # UNVERIFIED: run scripts/probe_cohere_v4.py first
}
COHERE_MAX_CHARS = MAX_CHARS["cohere-v3"]
V4_OUTPUT_DIM = 1024  # v4 supports 256/512/1024/1536; 1024 matches Titan v2


class EmbeddingCache:
    def __init__(self, path: Path = CACHE_DB):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute("""CREATE TABLE IF NOT EXISTS emb (
            key TEXT PRIMARY KEY, model TEXT, model_spec TEXT, input_type TEXT,
            text_sha256 TEXT, dim INTEGER, vec BLOB, billed_tokens INTEGER, created REAL)""")

    @staticmethod
    def key(model, input_type, text):
        """(model spec, input_type, text hash). No chunk config: see module docstring."""
        if input_type not in ("document", "query"):
            raise ValueError("input_type must be 'document' or 'query'")
        sha = hashlib.sha256(text.encode()).hexdigest()
        return json.dumps([MODEL_SPEC[model], input_type, sha]), sha

    def get(self, k) -> Optional[np.ndarray]:
        r = self.db.execute("SELECT vec FROM emb WHERE key=?", (k,)).fetchone()
        return None if r is None else np.frombuffer(r[0], dtype=np.float32)

    def put(self, k, model, it, sha, vec, billed):
        self.db.execute("INSERT OR REPLACE INTO emb VALUES (?,?,?,?,?,?,?,?,?)",
                        (k, model, MODEL_SPEC[model], it, sha, len(vec),
                         np.asarray(vec, dtype=np.float32).tobytes(), billed, time.time()))
        self.db.commit()

    def billed_tokens(self, model=None) -> int:
        q = "SELECT COALESCE(SUM(billed_tokens),0) FROM emb" + (" WHERE model=?" if model else "")
        return self.db.execute(q, (model,) if model else ()).fetchone()[0]


def _client():
    import boto3
    return boto3.client("bedrock-runtime", region_name=REGION)


def _invoke(client, model_id, body):
    r = client.invoke_model(modelId=model_id, body=json.dumps(body),
                            contentType="application/json", accept="application/json")
    hdr = r["ResponseMetadata"]["HTTPHeaders"]
    billed = int(hdr.get("x-amzn-bedrock-input-token-count", 0))
    return json.loads(r["body"].read()), billed


def _titan(client, texts: List[str], input_type: str):
    out = []
    for t in texts:
        body, billed = _invoke(client, MODELS["titan-v2"][0],
                               {"inputText": t, "dimensions": TITAN_DIM, "normalize": True})
        out.append((body["embedding"], billed))
    return out


def cohere_v4_body(texts: List[str], input_type: str) -> dict:
    """Request body for Cohere Embed v4. Shared with the probe script so the
    probe tests exactly what the index build will send."""
    return {"texts": texts, "input_type": COHERE_INPUT_TYPE[input_type],
            "embedding_types": ["float"], "output_dimension": V4_OUTPUT_DIM,
            "truncate": "NONE"}


def _cohere_call(client, model_key, texts, body):
    body, billed = _invoke(client, MODELS[model_key][0], body)
    embs = body["embeddings"]
    if isinstance(embs, dict):  # embedding_types response shape
        embs = embs["float"]
    if len(embs) != len(texts):
        raise RuntimeError(f"{model_key}: sent {len(texts)} texts, got {len(embs)} vectors")
    per = billed // max(len(texts), 1)  # batch billed total, split evenly (approximate)
    return [(e, per) for e in embs]


def cohere_v3_body(texts: List[str], input_type: str) -> dict:
    """Request body for Cohere Embed English v3 (shared with the probe script)."""
    return {"texts": texts, "input_type": COHERE_INPUT_TYPE[input_type], "truncate": "NONE"}


BODY_BUILDERS = {"cohere-v3": cohere_v3_body, "cohere-v4": cohere_v4_body}


def _cohere_v3(client, texts: List[str], input_type: str):
    return _cohere_call(client, "cohere-v3", texts, cohere_v3_body(texts, input_type))


def _cohere_v4(client, texts: List[str], input_type: str):
    return _cohere_call(client, "cohere-v4", texts, cohere_v4_body(texts, input_type))


ADAPTERS = {"titan-v2": _titan, "cohere-v3": _cohere_v3, "cohere-v4": _cohere_v4}


def check_lengths(texts: List[str], model: str) -> None:
    lim = MAX_CHARS[model]
    if lim is None:
        raise RuntimeError(f"{model}: per-text limit not verified empirically; "
                           "run scripts/probe_cohere_v4.py and set MAX_CHARS")
    over = [len(t) for t in texts if len(t) > lim]
    if over:
        raise ValueError(f"{model}: {len(over)} texts exceed {lim} chars (max {max(over)}); "
                         "refusing to let the API truncate silently")


def embed(texts: List[str], *, model: str, input_type: str,
          cache: Optional[EmbeddingCache] = None, dry_run: bool = False) -> np.ndarray:
    """Return float32 [n, d]. input_type must be 'document' or 'query' (required)."""
    if input_type not in ("document", "query"):
        raise ValueError("input_type must be 'document' or 'query'")
    check_lengths(texts, model)
    cache = cache or EmbeddingCache()
    keys = [cache.key(model, input_type, t) for t in texts]
    vecs = [cache.get(k) for k, _ in keys]
    # embed each distinct uncached text once, even if it repeats within this call
    first = {}
    for i, v in enumerate(vecs):
        if v is None:
            first.setdefault(keys[i][0], i)
    todo = sorted(first.values())
    if todo and dry_run:
        raise RuntimeError(f"dry_run: {len(todo)} texts not cached")
    if todo:
        client, batch = _client(), MODELS[model][2]
        for s in range(0, len(todo), batch):
            idx = todo[s:s + batch]
            res = ADAPTERS[model](client, [texts[i] for i in idx], input_type)
            for i, (v, billed) in zip(idx, res):
                k, sha = keys[i]
                cache.put(k, model, input_type, sha, v, billed)
                vecs[i] = np.asarray(v, dtype=np.float32)
        for i, v in enumerate(vecs):  # fill in-call repeats from their first occurrence
            if v is None:
                vecs[i] = vecs[first[keys[i][0]]]
    return np.vstack(vecs)
