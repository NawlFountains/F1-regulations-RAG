import re

from src.retrieval.retriver import retrieve
from src.prompts.prompt import build_messages, short_source
from src.llm.client import generate

def cited_ids(text):
    ids = []
    for group in re.findall(r"\[([^\]]+)\]", text):
        ids += re.findall(r"[A-Z]\d+(?:\.\d+)+", group)
    return list(dict.fromkeys(ids))

def ask(client, question, k=10):
    hits = retrieve(client, question, k=k)   # dense only
    answer = generate(build_messages(question, hits))

    by_id = {h.payload["article"]: h.payload for h in hits}
    cited = cited_ids(answer)
    sources = [
        {
            "clause": c,
            "source": short_source(by_id[c]["source"]),
            "section": by_id[c].get("section"),
            "page": by_id[c]["page_start"],
            "text": by_id[c]["text"],
        }
        for c in cited if c in by_id
    ]
    return {
        "answer": answer,
        "sources": sources,
        "unverified_citations": [c for c in cited if c not in by_id],
    }