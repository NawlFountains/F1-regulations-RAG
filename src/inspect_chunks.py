from ingestion.ingestion import load_directory
from chunking.chunking import split_into_clauses

import numpy as np
from embeddings.embedder import embed_chunks, embed_query, build_embed_text, get_model


# Skip index pages, which are not part of the regulations text. The index page number is different for each PDF, so we need to hardcode it here.
INDEX_PAGES = {
    "FIA 2026 F1 Regulations - Section A [General Provisions] - Iss 03 - 2026-06-25-1.pdf": 4,   # last index page
    "FIA 2026 F1 Regulations - Section B [Sporting] - Iss 09 - 2026-10-01 copy.pdf": 3,
    "FIA 2026 F1 Regulations - Section C [Technical] - Iss 21 - 2026-10-19-1.pdf": 6,
    "FIA 2026 F1 Regulations - Section D [Financial - F1 Teams] - Iss 08 - 2026-10-01.pdf": 3,
    "FIA 2026 F1 Regulations - Section E [Financial – PU Manufacturers] - Iss 07 - 2026-10-19.pdf": 2,
    "FIA 2026 F1 Regulations - Section F [Operational] - Iss 11 - 2026-10-01.pdf": 2,
}

pages = load_directory(r"D:\programmingProyects\F1-Regulations-RAG\documents")
pages = [p for p in pages if p["page"] > INDEX_PAGES.get(p["source"], 0)]

# What does PyMuPDF actually emit? Look at the raw text of one page.
print(repr(pages[10]["text"][:400]))

chunks = split_into_clauses(pages)
print(f"{len(chunks)} chunks\n")

# 1) The ID sequence: look for gaps, repeats, or out-of-order numbers
print([(c["article"], c["page_start"]) for c in chunks[:60]])

# 2) A few full chunks, to judge them by eye
for c in chunks[20:26]:
    print("-" * 60)
    print(c["article"], "|", c["section"], "| p.", c["page_start"])
    print(c["text"])

# 3) Size distribution: tiny or huge chunks usually mean a regex problem
sizes = sorted(len(c["text"]) for c in chunks)
print("min / median / max chars:", sizes[0], sizes[len(sizes)//2], sizes[-1])

# Print the chunk with the maximum size, to see if it looks like a regex problem.
print("-" * 60)
print(chunks[sizes.index(max(sizes))]["article"], "|", chunks[sizes.index(max(sizes))]["section"], "| p.", chunks[sizes.index(max(sizes))]["page_start"])
print(chunks[sizes.index(max(sizes))]["text"])

# Print chunk with article E3.1.1
for c in chunks:
    if c["article"] == "E3.1.1":
        print("-" * 60)
        print(c["article"], "|", c["section"], "| p.", c["page_start"])
        print(c["text"])