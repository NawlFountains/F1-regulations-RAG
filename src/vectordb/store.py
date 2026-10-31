from pathlib import Path
from qdrant_client import QdrantClient, models

COLLECTION = "f1_regs"
ROOT = Path(__file__).resolve().parents[2]     

def get_client(path=ROOT / "qdrant_data"):
    return QdrantClient(path=str(path))

def build_collection(client, chunks, embs):
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION,
        vectors_config=models.VectorParams(size=embs.shape[1], distance=models.Distance.COSINE),
    )
    client.upload_points(
        COLLECTION,
        points=[
            models.PointStruct(
                id=i,
                vector=embs[i].tolist(),
                payload={
                    "source": c["source"],
                    "article": c["article"],
                    "section": c.get("section"),
                    "page_start": c["page_start"],
                    "text": c["text"],
                },
            )
            for i, c in enumerate(chunks)
        ],
    )