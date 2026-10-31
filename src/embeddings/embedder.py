from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def build_embed_text(chunk):
    # keys from your current chunker: "article" = clause ID, "section" = parent title
    header = " - ".join(x for x in [chunk["article"], chunk.get("section")] if x)
    return f'{header}\n{chunk["text"]}'

def embed_chunks(chunks, batch_size=32):
    texts = [build_embed_text(c) for c in chunks]
    return get_model().encode(
        texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True
    )

def embed_query(query):
    return get_model().encode(QUERY_PREFIX + query, normalize_embeddings=True)