import numpy as np
from sentence_transformers import CrossEncoder
from embeddings.embedder import embed_query, build_embed_text
from vectordb.store import COLLECTION

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("BAAI/bge-reranker-base", max_length=512)
    return _reranker

def retrieve(client, query, k=10, rerank=False, candidates=20):
    hits = client.query_points(
        COLLECTION,
        query=embed_query(query).tolist(),
        limit=candidates if rerank else k,
    ).points
    if not rerank:
        return hits
    scores = get_reranker().predict([(query, build_embed_text(h.payload)) for h in hits])
    return [hits[i] for i in np.argsort(-scores)[:k]]