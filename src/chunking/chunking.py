import re

# Letter + number + at least one ".number", at the start of a line: F4.3, F4.3.1
ID_RE = re.compile(r"^\s*([A-Z]\d+(?:\.\d+)+)\b[ \t]*(.*)$")
APPENDIX_RE = re.compile(r"^APPENDIX\b")

def _depth(clause_id):
    return clause_id.count(".")

def split_into_clauses(pages):
    chunks, current = [], None

    def close():
        if current and current["text"].strip():
            current["text"] = current["text"].strip()
            chunks.append(current)

    for page in pages:
        # new document: close out the previous one
        if current and current["source"] != page["source"]:
            close()
            current = None

        for line in page["text"].splitlines():
            if APPENDIX_RE.match(line.strip()):
                close()
                current = None
                continue

            m = ID_RE.match(line)
            
            if m:
                close()
                clause_id, rest = m.groups()
                current = {
                    "source": page["source"],
                    "page_start": page["page"],
                    "article": clause_id,
                    "section": None,
                    "text": rest + "\n",
                }
            elif current:
                current["text"] += line + "\n"

    close()

    # attach the parent section title (F4.3 -> "RWTT Permitted technology")
    by_id = {(c["source"], c["article"]): c for c in chunks}
    for c in chunks:
        if _depth(c["article"]) >= 2:
            parent = by_id.get((c["source"], c["article"].rsplit(".", 1)[0]))
            if parent:
                c["section"] = parent["text"].splitlines()[0].strip()

    return chunks