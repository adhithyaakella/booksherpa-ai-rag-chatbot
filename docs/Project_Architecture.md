# BookSherpa AI: Project Journey & Architecture 🚀

**Date**: January 5, 2026
**Version**: 4.0

This document outlines the complete development journey of the **BookSherpa AI** application, from a basic document chatbot to an advanced, pedagogical "AI Tutor" powered by State-of-the-Art RAG techniques.

---

## 🏗️ Phase 1: The Foundation (Basic RAG)
**Goal**: Build a functional Chatbot that can answer questions based on a specific PDF Textbook.

### Key Implementations
1.  **Ingestion Pipeline (`app/ingest.py`)**:
    *   **PDF Loading**: Used `PyMuPDF` and `Unstructured` to read raw text.
    *   **Chunking**: Implemented `RecursiveCharacterTextSplitter` to break the book into manageable 1000-character chunks with overlap.
    *   **Vector Database**: Chose **FAISS** (Facebook AI Similarity Search) for fast local storage of embeddings.
    *   **Embeddings**: Used `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) to convert text to vectors.

2.  **QA Engine (`app/rag_qa.py`)**:
    *   **LLM**: Integrated **OpenAI GPT-4o-mini** for cost-effective, high-intelligence reasoning.
    *   **Retrieval Chain**: Built a standard "Stuff" chain: Retrieve Top 5 chunks -> Paste into Prompt -> Ask LLM.

3.  **Basic UI**:
    *   A simple **Streamlit** chat interface.

---

## 👩‍🏫 Phase 2: The Teacher Persona (Pedagogical AI)
**Goal**: Transform the bot from a passive search engine into an active *Teacher* and *Study Guide*.

### Key Implementations
1.  **Chapter Summarization**:
    *   **Metadata Enrichment**: Modified `ingest.py` to tag every chunk with its "Chapter Name" using Regex.
    *   **Summarizer Tab**: Added a dedicated feature where users can ask for "Chapter 3 Summary" and the AI retrieves only chunks from that specific chapter.

2.  **Multimodal Image Support**:
    *   **Extraction**: Processed the PDF to extract images and save them as `.png` files.
    *   **Linking**: Mapped every image to the page text it appeared on.
    *   **Display**: When the AI retrieves a text chunk that has an image, the image is automatically displayed in the chat to provide visual context.

3.  **Interactive Quiz Mode**:
    *   **JSON Output**: Instructed the LLM to output questions in strict JSON format.
    *   **UI**: Rendered these questions as interactive Radio Buttons instead of just text, allowing users to test themselves.

4.  **Session Persistence**:
    *   Integrated `SQLChatMessageHistory` (SQLite) so users can close the browser and resume their conversation later by entering their User ID.

---

## 🧠 Phase 3: UX & conversational Refinements
**Goal**: Polish the user experience to make it feel seamless and professional.

### Key Implementations
1.  **Conversational Tutor Mode**:
    *   Replaced the rigid "Quiz Form" with a natural chat.
    *   **Intent Detection**: If a user says "Switch to Chapter 5", the frontend detects this and resets the Tutor's context automatically.

2.  **Design Unification**:
    *   Ensured all three tabs (Chat, Tutor, Summarizer) use a consistent **bottom-docked input bar**, fixing early layout issues.

3.  **Verification Metadata**:
    *   Every retrieved image now displays its **Page Number** and **Source Filename** (e.g., "Page 45 - transformers.pdf"), building trust with the user.

---

## ⚡ Phase 4: Advanced RAG (The "Brain" Upgrade)
**Goal**: Solve the "Lost in the Middle" problem and handle technical queries (Acronyms) where basic Semantic Search failed.

### The Problem
*   **Semantic Search Failure**: Searching for specific acronyms like "**GLUE**" (a benchmark) failed because the vector embedding for "GLUE" (the word) didn't match the concept "General Language Understanding Evaluation".
*   **Ranking Failure**: The correct answer often appeared at rank #10, but we were only sending the Top 5 to the AI.

### The Solution (Key Upgrades)
1.  **Hybrid Search (Step 1)**:
    *   **BM25 (Keyword Search)**: Added a classic search engine layer that matches *exact words*.
    *   **Ensemble**: Combined BM25 + FAISS. Now, if you search "GLUE", BM25 grabs it instantly even if the semantic meaning is vague.

2.  **Cross-Encoder Re-Ranking (Step 2)**:
    *   **Top-20 Retrieval**: We now fetch a broad net of **20 candidates**.
    *   **The Re-Ranker**: Integrated `cross-encoder/ms-marco-MiniLM-L-6-v2`. This is a specialized model that "reads" the User Question and Candidate A side-by-side and outputs a relevance score (0-1).
    *   **Top-5 Selection**: We pick the absolute best 5 from the 20.
    *   **Technical Adapter**: Wrote a custom `HFCrossEncoderAdapter` to bridge compatibility issues between LangChain Core and Community libraries.

### Results
*   **Robustness**: The system now handles vague conceptual questions (via FAISS) AND specific technical keyword lookups (via BM25) with high precision.
*   **Latency**: Slightly increased (~0.6s) for much higher answer quality.

---

## 🗺️ Summary of Tech Stack
*   **Frontend**: Streamlit
*   **LLM**: OpenAI GPT-4o-mini
*   **Vector Store**: FAISS
*   **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
*   **Re-Ranker**: MS-MARCO Cross-Encoder
*   **Orchestration**: LangChain
*   **Database**: SQLite (History)
