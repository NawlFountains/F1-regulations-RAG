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
    
    extracted_texts = []
    for file in directory.glob("*.pdf"):
        extracted_texts.extend(extract_text(file))
    
    return extracted_texts


extracted_texts = load_directory("D:\programmingProyects\F1-Regulations-RAG\documents")

regulations_texts = [text for text in extracted_texts if 'FIA 2026 F1 Regulations' in text['source']]

print(f"Extracted {len(regulations_texts)} pages from FIA 2026 F1 Regulations.")

print("Sample extracted text from the first page:")
print(regulations_texts[0]['text'][:500])