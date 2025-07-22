import os
import sys
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv

# Ensure the backend 'app' directory is on the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.rag_qa import conversational_chain, get_session_history

load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="BookSherpa AI - Interactive Q&A", page_icon="📚", layout="wide"
)

st.title("📚 BookSherpa AI — Q&A Chatbot")
st.markdown("Ask questions and get instant answers from your indexed knowledge base.")

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Feel free to ask any question about the uploaded knowledge base.",
        }
    ]

# Display previous interactions
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")

# Chat input
user_input = st.chat_input("Type your question...")

if user_input:
    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True, key=f"msg_user_{len(st.session_state.messages)}")
    # Get answer from RAG pipeline
    with st.spinner("Finding your answer..."):
        try:
            result = conversational_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "default-session"}},
            )
            answer = result["answer"]
        except Exception as e:
            answer = f"Sorry, there was an error: {e}"
    # Save answer to history and display
    st.session_state.messages.append({"role": "assistant", "content": answer})
    message(
        answer, is_user=False, key=f"msg_assistant_{len(st.session_state.messages)}"
    )

# Footer
st.markdown("---")
st.markdown("*Powered by LangChain, FAISS, and Groq* 🚀")
