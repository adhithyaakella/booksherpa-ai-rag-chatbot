import os
import sys
import uuid
import streamlit as st
from dotenv import load_dotenv

# Ensure the backend 'app' directory is on the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.rag_qa import conversational_chain, generate_quiz, summarize_chapter, create_tutor_chain, launch_dashboard

load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="BookSherpa AI - Interactive Q&A", page_icon="📚", layout="wide"
)

st.title("📚 BookSherpa AI")
st.markdown("Your AI companion for studying *Natural Language Processing with Transformers*.")

# --- Tabs ---
tab_chat, tab_quiz, tab_summary = st.tabs(["💬 Chat", "🎓 Quiz Mode", "📖 Summarizer"])

# --- Session Management ---
# Sidebar for Persistence
with st.sidebar:
    st.header("👤 Profile")
    user_id = st.text_input("User ID (to save history)", value="default_user")
    if user_id:
        st.session_state.session_id = user_id
    st.info(f"Session ID: {st.session_state.session_id}")
    
    st.divider()
    # st.header("📊 Observability")
    # TruLens Disabled due to dependency conflict


if "session_id" not in st.session_state:
    st.session_state.session_id = user_id if user_id else str(uuid.uuid4())

# --- TAB 1: Chat Interface ---
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Ask me anything about the book."}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "images" in message and message["images"]:
                with st.expander("🖼️ Visual Context"):
                    cols = st.columns(len(message["images"]))
                    for i, img_path in enumerate(message["images"]):
                        with cols[i]:
                            # Handle both old (string) and new (dict) formats
                            if isinstance(img_path, dict):
                                st.image(img_path["path"], caption=img_path["caption"], width="stretch")
                            else:
                                st.image(img_path, width="stretch")

    # Chat input
    if prompt := st.chat_input("Ask a question about transformers..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    config = {"configurable": {"session_id": st.session_state.session_id}}
                    response = conversational_chain.invoke({"input": prompt}, config=config)
                    answer = response["answer"]
                    st.markdown(answer)
                    
                    # Check for images
                    found_images = []
                    if "context" in response:
                        seen = set()
                        for doc in response["context"]:
                            img = doc.metadata.get("image_path")
                            if img and img not in seen:
                                seen.add(img)
                                # Extract metadata for validation
                                page = doc.metadata.get("page", "?")
                                source = os.path.basename(doc.metadata.get("source", "PDF"))
                                caption = f"Page {page} ({source})"
                                found_images.append({"path": img, "caption": caption})

                    if found_images:
                        with st.expander("🖼️ Visual Context", expanded=True):
                            cols = st.columns(len(found_images))
                            for i, img_path in enumerate(found_images):
                                with cols[i]:
                                    # Handle both old (string) and new (dict) formats
                                    if isinstance(img_path, dict):
                                        st.image(img_path["path"], caption=img_path["caption"], width="stretch")
                                    else:
                                        st.image(img_path, caption="Reference", width="stretch")

                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "images": found_images
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: Tutor Mode (Conversational) ---
with tab_quiz:
    st.header("👩‍🏫 AI Tutor")
    # Clean UI: No top inputs
    
    # State for Tutor
    if "tutor_active" not in st.session_state:
        st.session_state.tutor_active = False # Tracks if a chain is live
    
    # We need a separate message history list for the frontend display
    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = [
            {"role": "assistant", "content": "Hello! I am your AI Tutor.\nType a topic or chapter to start your lesson (e.g., *'Chapter 4'*, *'Attention'*)."}
        ]

    # Helper to clean/detect intent
    def is_switch_command(text):
        triggers = ["switch to", "quiz me on", "change topic", "start a quiz", "new lesson", "stop"]
        return any(t in text.lower() for t in triggers)

    # Display Tutor History
    for msg in st.session_state.tutor_messages:
         with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if user_input := st.chat_input("Type your answer or a new topic...", key="tutor_input"):
        st.session_state.tutor_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # LOGIC:
                    # 1. If command -> Reset and Start
                    # 2. If not active -> Treat as Topic -> Start
                    # 3. If active -> Treat as Answer -> Continue
                    
                    response_text = ""
                    
                    if is_switch_command(user_input) or not st.session_state.tutor_active:
                        # START NEW SESSION
                        topic = user_input.replace("switch to", "").replace("quiz me on", "").strip()
                        if not topic: topic = "General"
                        
                        st.session_state.tutor_topic = topic
                        st.session_state.tutor_active = True
                        # New ID for new context
                        st.session_state.tutor_session_id = f"{st.session_state.session_id}_tutor_{uuid.uuid4().hex[:4]}"
                        
                        # Create chain & Get first question
                        tutor_chain = create_tutor_chain(topic)
                        cfg = {"configurable": {"session_id": st.session_state.tutor_session_id}}
                        response_text = tutor_chain.invoke({"input": f"Start a new lesson on {topic}."}, config=cfg).content
                        
                    else:
                        # CONTINUE SESSION
                        tutor_chain = create_tutor_chain(st.session_state.tutor_topic)
                        cfg = {"configurable": {"session_id": st.session_state.tutor_session_id}}
                        response_text = tutor_chain.invoke({"input": user_input}, config=cfg).content

                    st.markdown(response_text)
                    st.session_state.tutor_messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 3: Summary Interface ---
with tab_summary:
    st.header("📖 Chapter Summarizer")
    # Clean UI: No top inputs
    
    if "summary_messages" not in st.session_state:
        st.session_state.summary_messages = [
            {"role": "assistant", "content": "Enter a Chapter Name (e.g., *'Chapter 1'*) to get a summary."}
        ]

    # Display History
    for msg in st.session_state.summary_messages:
         with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input
    if chapter_input := st.chat_input("Enter Chapter Name...", key="summary_input"):
        st.session_state.summary_messages.append({"role": "user", "content": chapter_input})
        with st.chat_message("user"):
            st.markdown(chapter_input)
            
        with st.chat_message("assistant"):
            with st.spinner(f"Reading and summarizing '{chapter_input}'..."):
                try:
                    summary_text = summarize_chapter(chapter_input)
                    st.markdown(summary_text)
                    st.session_state.summary_messages.append({"role": "assistant", "content": summary_text})
                except Exception as e:
                    st.error(f"Error: {e}")
                except Exception as e:
                    st.error(f"Summarization failed: {e}")
    
    if "current_summary" in st.session_state:
        st.divider()
        st.markdown(f"### Summary of {chapter_input}")
        st.markdown(st.session_state["current_summary"])

# --- Footer ---
st.markdown("---")
st.markdown("*Powered by LangChain, FAISS, and OpenAI* 🚀")
