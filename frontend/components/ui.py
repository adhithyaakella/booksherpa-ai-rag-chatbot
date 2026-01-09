import streamlit as st
import os

def apply_custom_css():
    """Injects custom CSS for the application."""
    # Currently reverts to standard styling, but kept for future extensibility.
    pass

def render_welcome_message():
    """Renders the Empty State / Welcome Screen."""
    st.info("👋 Welcome to BookSherpa AI!")
    st.markdown("""
    ### 🚀 Get Started
    Your library is currently empty. To start chatting:
    
    1.  Open the **sidebar** (↖️).
    2.  **Upload a PDF** textbook.
    3.  Click **"🔄 Build Knowledge Base"**.
    
    Once the AI learns your book, this chat will unlock! 🔓
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/748/748606.png", width=150, caption="Waiting for books...")
