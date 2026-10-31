import os
import streamlit as st

from src.embeddings.embedder import get_model
from src.vectordb.store import get_client
from src.rag import ask
from src.vectordb.store import COLLECTION

st.set_page_config(page_title="F1 Regulations RAG", page_icon="🏁")

# On Streamlit Cloud the key comes from st.secrets; locally it comes from .env
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

@st.cache_resource
def load_resources():
    get_model()                 # load the embedder once per server, not once per question
    return get_client()

client = load_resources()

if not client.collection_exists(COLLECTION):
    st.error("The index hasn't been built yet. Run the evaluation script once to build it.")
    st.stop()

EXAMPLES = [
    "What happens if two drivers finish with the same number of points?",
    "Can a car be refueled during a race?",
    "Can lapped cars overtake the safety car?",
    "What's the cost cap for 2026?",
]

st.title("F1 Regulations Q&A")
st.caption("Answers come only from the FIA 2026 F1 Regulations, with the clauses they cite.")

st.sidebar.header("Try an example")
question = st.chat_input("Ask about the regulations...")
for ex in EXAMPLES:
    if st.sidebar.button(ex):
        question = ex

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the regulations..."):
            try:
                result = ask(client, question)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        st.markdown(result["answer"])

        if result["unverified_citations"]:
            st.warning(
                "The answer cites clauses that were not retrieved: "
                + ", ".join(result["unverified_citations"])
            )

        if result["sources"]:
            st.subheader("Sources")
            for s in result["sources"]:
                label = f'{s["clause"]} · {s["source"]} · p. {s["page"]}'
                with st.expander(label):
                    if s["section"]:
                        st.caption(s["section"])
                    st.text(s["text"])