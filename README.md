# BookSherpa AI 🏔️📚

**BookSherpa AI** is an advanced, pedagogical "AI Tutor" designed to help you master complex textbooks. Unlike standard chatbots, it actively teaches you, quizzes you, and uses State-of-the-Art **Hybrid RAG** to find the exact information you need.

---

## 🚀 Key Features

### 🧠 Advanced RAG Engine
*   **Hybrid Search**: Combines **Semantic Search** (FAISS) with **Keyword Search** (BM25) to understand both *concepts* and specific *acronyms/terms*.
*   **Cross-Encoder Re-Ranking**: Uses a specialized model (`ms-marco-MinLM-L-6-v2`) to "grade" the top 20 results and select the absolute best 5 for the answer.
*   **Multimodal**: Automatically extracts and displays **Images/Diagrams** from the textbook relevant to your question.

### �‍🏫 Pedagogical Modes
1.  **💬 Chat Mode**: Ask anything. The AI acts as a helpful Professor, suggesting follow-up topics.
2.  **🎓 Quiz Mode**: Generates interactive 10-question quizzes on any chapter or topic. Includes immediate feedback and explanations.
3.  **🗣️ Tutor Mode**: A Socratic conversation. The AI asks you one question at a time to check your understanding, adapting to your answers.
4.  **📖 Summarizer**: Generates high-level summaries of specific chapters.

### 🛠️ Technical Highlights
*   **Modular Architecture**: Clean separation of concerns (`retrieval`, `services`, `features`).
*   **Session Persistence**: Remembers your chat history even if you close the browser (SQLite backed).
*   **Metadata Enrichment**: chunks are tagged with Chapter names for filtered retrieval.

---

## 🗂️ Project Structure

```
booksherpa-ai/
├── app/                  # Backend Logic
├── frontend/
│   ├── components/       # UI Modules (Sidebar, Styles)
│   └── BookSherpa_AI.py  # Main Entry Point
├── data/                 # Source PDFs
├── docs/                 # Documentation
├── scripts/              # Utility Scripts (Eval, Tools)
├── tests/                # Unit Tests
└── vectorstore/          # FAISS Index
```

---

## ⚡ Getting Started

### 1. Prerequisite
Ensure you have Python 3.10+ installed.

### 2. Setup Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
# Manually install RAG specifics if needed
pip install rank_bm25 sentence-transformers langchain_huggingface
```

### 4. Configure Environment
Create a `.env` file in the root:
```env
OPENAI_API_KEY=sk-your-key-here
```
*(Note: This project uses OpenAI GPT-4o-mini for reasoning)*

### 5. Ingest Data (Two Options)
**Option A (Easy UI):**
1.  Launch the app (`step 6`).
2.  Use the **"Library Manager"** in the sidebar to upload PDFs.
3.  Click "🔄 Build Knowledge Base".

**Option B (CLI):**
Place your PDF in `data/` and run:
```bash
python app/ingest.py
```

### 6. Run the App
```bash
python -m streamlit run frontend/BookSherpa_AI.py
```
Visit `http://localhost:8501`.

### 7. Evaluation (Optional)
To verify the RAG pipeline's accuracy using **LLM-as-a-Judge**:
```bash
python scripts/run_eval.py
```
This runs a test suite of questions and grades the answers (1-5) using GPT-4o-mini.

---

## 📚 Documentation
For a deep dive into the architecture and journey from Phase 1 to Phase 4, see:
👉 [Project Architecture & Journey](docs/Project_Architecture.md)

For performance metrics and RAG evaluation:
👉 [Advanced RAG Log](docs/Advanced_RAG_Log.md)

---

## �️ Stack
*   **Framework**: LangChain, Streamlit
*   **LLM**: OpenAI GPT-4o-mini
*   **Vector DB**: FAISS
*   **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
*   **Re-Ranker**: Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
*   **Database**: SQLite

---
*Built with ❤️ by Adhithya Akella*