import streamlit as st
import os
import sys
import shutil
import uuid
from app import rag_qa

def render_sidebar(project_root):
    """Renders the sidebar with File Uploader, Reset, and Ingest controls."""
    with st.sidebar:
        st.header("👤 Profile")
        user_id = st.text_input("User ID (to save history)", value="default_user")
        if user_id:
            st.session_state.session_id = user_id
        st.info(f"Session ID: {st.session_state.session_id}")
        
        st.divider()
        st.header("📚 Library Manager")

        # 1. File Uploader
        uploaded_files = st.file_uploader(
            "Upload Textbook (PDF)", 
            type=["pdf"], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Ensure data dir exists
                data_dir = os.path.join(project_root, "data")
                os.makedirs(data_dir, exist_ok=True)
                
                save_path = os.path.join(data_dir, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"Saved {len(uploaded_files)} file(s) to library.")

        # 2. Reset Library Button
        if st.button("🗑️ Reset Library"):
            try:
                # Clear data directory
                data_dir = os.path.join(project_root, "data")
                if os.path.exists(data_dir):
                    shutil.rmtree(data_dir)
                    os.makedirs(data_dir) # Recreate empty
                
                # Clear vectorstore
                vectorstore_dir = os.path.join(project_root, "vectorstore")
                if os.path.exists(vectorstore_dir):
                    shutil.rmtree(vectorstore_dir)

                # Clear static images
                images_dir = os.path.join(project_root, "frontend", "static", "images")
                if os.path.exists(images_dir):
                    shutil.rmtree(images_dir)
                    os.makedirs(images_dir) # Recreate empty for next ingest
                    
                # Clear Session State (Chat History) to remove old context
                st.session_state.clear()
                
                st.warning("Library and Knowledge Base cleared. Please upload new files.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset library: {e}")

        # 3. Ingestion Trigger
        if st.button("🔄 Build Knowledge Base"):
            with st.status("Building Knowledge Base...", expanded=True) as status:
                st.write("Initializing Ingestion Engine...")
                try:
                    import subprocess
                    # Run ingest.py as a subprocess
                    cmd = [sys.executable, os.path.join(project_root, "app", "ingest.py"), "--force"]
                    
                    process = subprocess.Popen(
                        cmd, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True,
                        encoding='utf-8',
                        cwd=project_root
                    )
                    
                    # Stream output
                    log_container = st.empty()
                    full_log = ""
                    
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        if line:
                            full_log += line
                            log_container.code(full_log[-2000:], language="bash")

                    if process.returncode == 0:
                        status.update(label="✅ Knowledge Base Updated!", state="complete", expanded=False)
                        
                        # 🚀 Hot Reload Logic
                        try:
                            rag_qa.reload_chain()
                            st.success("Ingestion Complete! Knowledge Base Reloaded.")
                        except Exception as e:
                            st.warning(f"Ingestion done, but reload failed: {e}. Please restart app.")

                        st.balloons()
                    else:
                        status.update(label="❌ Ingestion Failed", state="error")
                        st.error("Error building index. Check console logs.")
                        st.code(process.stderr.read())
                        
                except Exception as e:
                    st.error(f"Failed to run ingestion: {e}")

        st.divider()
        return user_id # return for session initialization if needed
