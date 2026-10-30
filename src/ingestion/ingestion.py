import pymupdf as fitz
from pathlib import Path

def extract_text(file_path):
    with fitz.open(file_path) as doc:
        return [
            {"source": Path(file_path).name, "page": i + 1, "text": page.get_text()} 
            for i, page in enumerate(doc)
        ]

def load_directory(directory_path):
    directory = Path(directory_path)
    if not directory.is_dir():
        raise ValueError(f"{directory_path} is not a valid directory.")
    
    pages = []
    for file in directory.glob("*.pdf"):
        pages.extend(extract_text(file))
    
    return pages


if __name__ == "__main__":
    pages = load_directory(r"D:\programmingProyects\F1-Regulations-RAG\documents")
    regs = [p for p in pages if "FIA 2026 F1 Regulations" in p["source"]]
    print(f"Extracted {len(regs)} pages.")
    print(regs[0]["text"][:500])