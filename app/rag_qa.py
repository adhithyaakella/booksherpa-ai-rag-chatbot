import os

# Compute absolute path:
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORSTORE_PATH = os.path.join(PROJECT_ROOT, "vectorstore", "db_faiss")

import re
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# TruLens imports
from trulens.core import TruSession, Feedback, Provider
from trulens.apps.langchain import TruChain
from trulens.dashboard import run_dashboard

# LangSmith tracing imports
from langchain_core.callbacks.manager import CallbackManager
from langchain.callbacks.tracers.langchain import LangChainTracer

load_dotenv()


# 1. VERIFY ENVIRONMENT VARIABLES
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ Missing GROQ_API_KEY in .env")
    exit(1)

if not os.getenv("LANGSMITH_API_KEY"):
    print("❌ Missing LANGSMITH_API_KEY in .env")
    exit(1)

# 2. ENABLE LANGSMITH TRACING
os.environ["LANGSMITH_TRACING"] = "true"
# Initialize tracer and callback manager
tracer = LangChainTracer()
callback_manager = CallbackManager(handlers=[tracer])

# 3. INITIALIZE TRULENS SESSION
session = TruSession()

# 4. BUILD RAG CHAIN WITH LANGSMITH CALLBACKS
VECTORSTORE_PATH = "vectorstore/db_faiss"

# Embeddings & vectorstore
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH, embedding_model, allow_dangerous_deserialization=True
)

# LLM
llm = ChatGroq(api_key=GROQ_API_KEY, model_name="compound-beta-mini")

# Prompts
CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given the conversation and a follow-up question, rephrase it as a standalone question.",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer using only the context below. If unsure, say 'I don't know'.\n\nContext:\n{context}",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Retriever & chains
retriever = create_history_aware_retriever(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    prompt=CONDENSE_PROMPT,
)
combine_docs_chain = create_stuff_documents_chain(llm, QA_PROMPT)

retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

# 5. MEMORY WRAP
session_store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


conversational_chain = RunnableWithMessageHistory(
    retrieval_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


# 6. LOCAL FEEDBACK FUNCTIONS
class LocalProvider(Provider):
    def response_length_check(self, inp, out):
        wc = len(out.split())
        if wc < 10:
            return 0.2
        if wc > 500:
            return 0.6
        return 1.0

    def keyword_presence(self, inp, out):
        stop = {"the", "a", "and", "of", "to", "is", "in", "on", "what", "how"}
        ins = set(w.lower().strip(".,!?") for w in inp.split()) - stop
        outs = set(w.lower().strip(".,!?") for w in out.split())
        return min(len(ins & outs) / max(len(ins), 1), 1.0)

    def completeness_check(self, inp, out):
        end = 1.0 if out.strip().endswith((".", "!", "?")) else 0.3
        parts = [s for s in re.split(r"[.!?]+", out) if len(s.strip()) > 5]
        struct = 1.0 if len(parts) >= 2 else 0.7 if parts else 0.3
        return (end + struct) / 2

    def informativeness(self, inp, out):
        low = ["i don't know", "i do not know", "not sure"]
        ol = out.lower()
        return 0.2 if any(p in ol for p in low) else 1.0


prov = LocalProvider()
fb_length = Feedback(prov.response_length_check, name="Length").on_input_output()
fb_keyword = Feedback(prov.keyword_presence, name="Keywords").on_input_output()
fb_complete = Feedback(prov.completeness_check, name="Completeness").on_input_output()
fb_info = Feedback(prov.informativeness, name="Informativeness").on_input_output()
feedbacks = [fb_length, fb_keyword, fb_complete, fb_info]

# 7. WRAP WITH TRUCHAIN & DASHBOARD
tru_app = TruChain(
    app=conversational_chain,
    app_name="booksherpa-rag",
    app_version="v1.0-local",
    feedbacks=feedbacks,
)

print("🚀 Launching TruLens Dashboard...")
run_dashboard(session=session)

# 8. CLI LOOP
if __name__ == "__main__":
    print("📚 BookSherpa AI + TruLens + LangSmith")
    print(
        "🔗 Dashboard:",
        os.environ.get("STREAMLIT_SERVER_PORT", "http://localhost:8501"),
    )
    session_id = "user-session"
    while True:
        q = input("🧠 You: ")
        if q.strip().lower() == "exit":
            break
        with tru_app as rec:
            res = conversational_chain.invoke(
                {"input": q}, config={"configurable": {"session_id": session_id}}
            )
        print(f"🤖 AI: {res['answer']}\n✅ Logged & traced\n")
    print("👋 Goodbye! View results in TruLens & LangSmith UI.")
