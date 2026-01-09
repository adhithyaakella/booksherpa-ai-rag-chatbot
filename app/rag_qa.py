# Main RAG & QA Controller
# This file aggregates modules to provide a unified API for the Frontend.

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Local Modules
from app.services import llm
from app.retrieval import retriever
from app.chat import get_session_history
# Optional Observability
from app.observability import get_recorder, launch_dashboard

# Re-export Features for Frontend
from app.features.quiz import generate_quiz
from app.features.summary import summarize_chapter
from app.features.tutor import create_tutor_chain

# --- Main Conversational Chain Setup ---

CONDENSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Given the conversation and a follow-up question, rephrase it as a standalone question."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful and knowledgeable Professor.
Your goal is not just to answer, but to teach.

Instructions:
1. Answer the user's question strictly using the provided context.
2. If the answer is not in the context, state "I cannot find this information in the uploaded book."
3. Do NOT use your own knowledge to answer questions about specific books.
4. Suggest 1-2 follow-up questions based ONLY on the context.

Context:
{context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# --- Main Conversational Chain Setup ---
conversational_chain = None

def build_chain(active_retriever):
    """Factory to create a new chain with the given retriever."""
    if not active_retriever:
        return None
        
    history_aware_retriever = create_history_aware_retriever(
        llm, active_retriever, CONDENSE_PROMPT
    )
    qa_chain = create_stuff_documents_chain(llm, QA_PROMPT)
    retrieval_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    # 🔎 Wrap with TruLens (if installed)
    retrieval_chain = get_recorder(retrieval_chain)

    chain_with_history = RunnableWithMessageHistory(
        retrieval_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return chain_with_history

# Initial Load
conversational_chain = build_chain(retriever)

def reload_chain():
    """Reloads the retriever from disk and rebuilds the global chain."""
    from app.retrieval import reload_retriever
    
    print("🔄 Rebuilding RAG Chain...")
    new_retriever = reload_retriever()
    
    global conversational_chain
    conversational_chain = build_chain(new_retriever)
    return conversational_chain

# For backward compatibility if main is run
if __name__ == "__main__":
    print("Please run via streamlit or verify_ scripts.")
