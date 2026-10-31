from vectordb.store import get_client
from rag import ask

client = get_client()
print("Ask about the regulations. Empty line or 'exit' to quit.")

try:
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in ("", "exit", "quit"):
            break
        try:
            result = ask(client, question)
        except Exception as e:      
            print(f"Error: {e}")
            continue

        print("\n" + result["answer"], "\n")
        for s in result["sources"]:
            print(f'  [{s["clause"]}] {s["source"]}, p. {s["page"]}')
        if result["unverified_citations"]:
            print("\nWARNING, cited but not retrieved:", result["unverified_citations"])
except (KeyboardInterrupt, EOFError):   
    pass
finally:
    client.close()