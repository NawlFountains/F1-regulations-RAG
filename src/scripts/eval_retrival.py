import numpy as np
from ingestion.ingestion import load_directory
from chunking.chunking import split_into_clauses
from embeddings.embedder import embed_chunks, embed_query
from vectordb.store import get_client, build_collection, COLLECTION
from retrieval.retriver import retrieve

EVAL = [
    ("What happens if two drivers finish with the same number of points?", "A2.1.4"),
    ("What are the maximum number of cars possible in a race?", "A2.1.3"),
    ("When a safety car is deployed?", "B5.13.1"),
    ("Can lapped cars overtake the safety car?", "B5.13.4"),
    ("What's the minimum weight of a car?", "C4.1"),
    ("Can a F1 team use near freezing fuel?", "C6.4.2"),
    ("Can a car be refueled during a race?", "C6.4.4"),
    ("Can a car finish without fuel?", "C6.5.2"),
    ("Can a car has assistance for acceleration?", "C8.6.4"),
    ("Are F1 radios made by teams or by suppliers?", "C8.8.1"),
    ("Can a radio be private?", "C8.8.2"),
    ("What's the cost cap for 2026?", "D4.1.2"),
    ("Is there a limit on the cost of a power unit?", "E2.3.1"),
]

# Skip index pages, which are not part of the regulations text. The index page number is different for each PDF, so we need to hardcode it here.
INDEX_PAGES = {
    "FIA 2026 F1 Regulations - Section A [General Provisions] - Iss 03 - 2026-06-25-1.pdf": 4,   # last index page
    "FIA 2026 F1 Regulations - Section B [Sporting] - Iss 09 - 2026-10-01": 3,
    "FIA 2026 F1 Regulations - Section C [Technical] - Iss 21 - 2026-10-19-1.pdf": 6,
    "FIA 2026 F1 Regulations - Section D [Financial - F1 Teams] - Iss 08 - 2026-10-01.pdf": 3,
    "FIA 2026 F1 Regulations - Section E [Financial – PU Manufacturers] - Iss 07 - 2026-10-19.pdf": 2,
    "FIA 2026 F1 Regulations - Section F [Operational] - Iss 11 - 2026-10-01.pdf": 2,
}

client = get_client()
if not client.collection_exists(COLLECTION):      # embed only on the first run
    pages = load_directory(r"D:\programmingProyects\F1-Regulations-RAG\documents")
    pages = [p for p in pages if p["page"] > INDEX_PAGES.get(p["source"], 0)]
    
    chunks = split_into_clauses(pages)
    build_collection(client, chunks, embed_chunks(chunks))

CONFIGS = {
    "dense":          dict(),
    "dense+rerank":   dict(rerank=True),
    "hybrid":         dict(hybrid=True),
    "hybrid+rerank":  dict(hybrid=True, rerank=True),
}

def recall_at_k(k, **opts):
    hits = 0
    for question, expected in EVAL:
        top = [h.payload["article"] for h in retrieve(client, question, k, **opts)]
        hits += expected in top
    return hits / len(EVAL)

for k in (3, 5, 10):
    row = " | ".join(f"{name}: {recall_at_k(k, **opts):.2f}" for name, opts in CONFIGS.items())
    print(k, row)

client.close()