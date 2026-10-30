# tests/test_chunking.py
from src.chunking.chunking import split_into_clauses

def page(text, n=1, source="doc.pdf"):
    return {"source": source, "page": n, "text": text}

def test_splits_clauses_and_attaches_section():
    pages = [page(
        "F4.3 RWTT Permitted technology\n"
        "The following restrictions apply during RWTT:\n"
        "F4.3.1 Only wind tunnels that use air are permitted.\n"
        "F4.3.2 Models must be scaled.\n"
    )]
    chunks = split_into_clauses(pages)
    ids = [c["article"] for c in chunks]
    assert ids == ["F4.3", "F4.3.1", "F4.3.2"]
    assert chunks[1]["section"] == "RWTT Permitted technology"

def test_clause_spanning_pages_stays_together():
    pages = [
        page("F4.3.1 Only wind tunnels that use air", n=1),
        page("at atmospheric pressure are permitted.", n=2),
    ]
    chunks = split_into_clauses(pages)
    assert len(chunks) == 1
    assert "atmospheric pressure" in chunks[0]["text"]
    assert chunks[0]["page_start"] == 1

def test_appendix_does_not_bleed_into_last_clause():
    pages = [
        page("F4.3.1 Only wind tunnels are permitted.\nAPPENDIX 1: DEFINITIONS\n", n=1),
        page("F1 Car: a car built to these regulations.\n", n=2),
    ]
    chunks = split_into_clauses(pages)

    assert len(chunks) == 1
    assert chunks[0]["article"] == "F4.3.1"
    assert "wind tunnels" in chunks[0]["text"]
    assert "DEFINITIONS" not in chunks[0]["text"]
    assert "F1 Car" not in chunks[0]["text"]   # definitions on the next page are dropped too

def test_number_alone_on_its_own_line():
    # PyMuPDF often emits the ID and the text on separate lines
    pages = [page("F4.3.1\nOnly wind tunnels are permitted.\n")]
    chunks = split_into_clauses(pages)
    assert chunks[0]["article"] == "F4.3.1"
    assert "wind tunnels" in chunks[0]["text"]