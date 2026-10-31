import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from embeddings.embedder import embed_query, build_embed_text
from vectordb.store import COLLECTION

_bm25 = None
_reranker = None

def _tokens(text):
    return re.findall(r"\w+", text.lower())

def _get_bm25(client):
    global _bm25
    if _bm25 is None:
        points, _ = client.scroll(COLLECTION, limit=100_000, with_payload=True, with_vectors=False)
        _bm25 = (BM25Okapi([_tokens(build_embed_text(p.payload)) for p in points]), points)
    return _bm25

def _bm25_search(client, query, n):
    bm25, points = _get_bm25(client)
    scores = bm25.get_scores(_tokens(query))
    return [points[i] for i in np.argsort(-scores)[:n]]

def _rrf(rankings, k=60):
    scores, by_id = {}, {}
    for ranking in rankings:
        for rank, p in enumerate(ranking):
            scores[p.id] = scores.get(p.id, 0) + 1 / (k + rank + 1)
            by_id[p.id] = p
    return [by_id[i] for i in sorted(scores, key=scores.get, reverse=True)]

def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("BAAI/bge-reranker-base", max_length=512)
    return _reranker

def retrieve(client, query, k=10, hybrid=False, rerank=False, pool=30, candidates=20):
    dense = client.query_points(
        COLLECTION, query=embed_query(query).tolist(), limit=pool
    ).points

    # 1) candidate list: dense alone, or dense + BM25 fused
    hits = _rrf([dense, _bm25_search(client, query, pool)]) if hybrid else dense

    # 2) optionally rerank the top candidates, otherwise just cut to k
    if not rerank:
        return hits[:k]
    hits = hits[:candidates]
    scores = _get_reranker().predict([(query, build_embed_text(h.payload)) for h in hits])
    return [hits[i] for i in np.argsort(-scores)[:k]]