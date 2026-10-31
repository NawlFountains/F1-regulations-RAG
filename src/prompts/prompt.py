import re

SYSTEM_PROMPT = """You answer question about the FIA Formula 1 regulations.

Rules:
- Use ONLY the numbered clauses provided in the context. Do not use outside knowledge about F1.
- After every claim, cite the clause ID in its own square brackets, like [A2.1.4] or [A2.1.4][B5.13.1]. Cite only IDs that appear in the context.
- If the clauses do not contain the answer, reply: "The provided regulations do not cover this." You may mention which clauses came closest.
- If clauses seem to conflict, say so and cite both.
- Be concise. Answer in the language of the question."""

def short_source(source):
    m = re.search(r"Section [A-Z] \[[^\]]*\]", source)
    return m.group(0) if m else source

def format_context(hits):
    blocks = []
    for h in hits:
        p = h.payload
        header = f'[{p["article"]}] {short_source(p["source"])}'
        if p.get("section"):
            header += f' | {p["section"]}'
        header += f' | p. {p["page_start"]}'
        blocks.append(f'{header}\n{p["text"]}')
    return "\n\n".join(blocks)

def build_messages(question, hits):
    user = f"Context clauses:\n\n{format_context(hits)}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]