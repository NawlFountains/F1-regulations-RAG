from src.ingestion.ingestion import load_directory
from src.ingestion.index_pages import INDEX_PAGES
from src.chunking.chunking import split_into_clauses
from src.embeddings.embedder import embed_chunks
from src.vectordb.store import get_client, build_collection, COLLECTION

pages = load_directory(r"D:\programmingProyects\F1-Regulations-RAG\documents")

missing = {p["source"] for p in pages} - INDEX_PAGES.keys()
assert not missing, f"No index-page entry for: {missing}"

pages = [p for p in pages if p["page"] > INDEX_PAGES[p["source"]]]
chunks = split_into_clauses(pages)
print(f"{len(chunks)} chunks")

client = get_client()
build_collection(client, chunks, embed_chunks(chunks))   # deletes and recreates the collection
print("points stored:", client.count(COLLECTION).count)
client.close()