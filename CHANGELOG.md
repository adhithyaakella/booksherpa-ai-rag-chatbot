# Changelog & Update History 📜

All notable changes to the **BookSherpa AI** project will be documented in this file.

## [Phase 11.0] - 2026-01-09
### Added
- **Query Expansion**: Implemented `MultiQueryRetriever` to generate 3 variations of user questions, aiming to improve recall for ambiguous queries.
- **Strict Mode**: Updated System Prompt to explicitly forbid answering from outside knowledge if context is found, reducing hallucinations.

## [Phase 10.0] - 2026-01-09
### Cleaned
- **Project Structure**: Created `scripts/` folder for utility scripts (`run_eval.py`).
- **Optimization**: Modularized `frontend` directory.

## [Phase 9.0] - 2026-01-09
### Added
- **Testing Suite**: Added `tests/` directory with `pytest` compatibility.
- **Unit Tests**: Added `test_config.py` and `test_chunking.py` to verify core logic.

## [Phase 8.0] - 2026-01-09
### Changed
- **Refactoring**: Split `BookSherpa_AI.py` into modular components (`sidebar.py`, `ui.py`).
- **Code Quality**: Reduced main file size by ~100 lines.

## [Phase 7.0] - 2026-01-08
### Added
- **UI Polish**: Injected custom CSS for modern chat bubbles and typography.
- **Empty State**: Added "Welcome Screen" for new users.
- **Visuals**: Cleaned up layout and icons.

## [Phase 6.0] - 2026-01-08
### Added
- **Library Manager**: Sidebar UI to upload PDFs directly to the `data/` folder.
- **Auto-Ingestion**: "Build Knowledge Base" button runs the ingestion pipeline from the browser with real-time logs.
- **LLM-as-a-Judge**: Automated quality evaluation script (`run_eval.py`).

## [Phase 4.0] - 2026-01-03
### Added
- **Hybrid Search**: Implemented `EnsembleRetriever` combining **BM25** (Keyword) and **FAISS** (Semantic).
- **Cross-Encoder Re-Ranking**: Integrated `cross-encoder/ms-marco-MiniLM-L-6-v2`.

### Removed
- **TruLens Observability**: Attempted integration but rolled back due to severe dependency conflict with LangChain (`ModuleNotFoundError`). Feature is disabled for stability.

## [Phase 3.4] - 2026-01-02
### Improved
- **Quiz Variety**: Implemented randomized context shuffling for the Tutor. Instead of always using the top-10 chunks (deterministic), we now fetch top-20 and randomly select 8. This ensures different questions generated for the same topic request.

## [Phase 3.3] - 2026-01-02
### Changed
- **Unified Chat Layout**: Refactored the **Summarizer** tab to use a conversational interface. Now, all three tabs (Chat, Tutor, Summary) use a consistent **bottom-docked input bar**.

## [Phase 3.2] - 2026-01-02
### Changed
- **Image Validation**: Images now display **Page Number** and **Source Filename** in the caption (e.g., "Page 45 (transformers.pdf)") to let users verify the context.
- **UI Layout**: Verified bottom-docked input across all tabs.

## [Phase 3.1] - 2026-01-02
### Fixed
- **Tutor Prompt Error**: Fixed `Input to ChatPromptTemplate is missing variables` by properly binding `topic` and `context` using `.partial()`.
- **UI Warnings**: Replaced deprecated `use_container_width` with `width="stretch"` in Streamlit image calls.

## [Phase 3] - 2026-01-01
### Added
- **Pure Chat Tutor**: Refactored the "AI Tutor" tab to remove forms. It is now a fully conversational interface.
- **Intent Detection**: The Tutor now detects commands like "Switch to Chapter 3" or "Quiz me on BERT" to reset context dynamically.
- **Documentation**: Created `docs/BookSherpa_Guide.md` for user-facing instructions.

## [Phase 2.2] - 2025-12-31
### Added
- **Conversational Tutor Chain**: Implemented `create_tutor_chain` in `rag_qa.py` to act as a Socratic teacher (asks 1 Q at a time, verifies answers).
- **Pedagogical Prompts**: Updated the main `QA_PROMPT` to suggest follow-up questions and guide the user proactively.

## [Phase 2.1] - 2025-12-31
### Added
- **Interactive Quiz**: Backend now returns structured JSON for quizzes. Frontend renders Radio Buttons for option selection.
- **Session Persistence**: Added a Sidebar Input for "User ID". Entering a name restores previous chat history (using `SQLChatMessageHistory`).

## [Phase 2.0] - 2025-12-31
### Added
- **Chapter Summarization**: New "Summarizer" tab. Users can input a chapter name to get a high-level summary.
    - *Technical*: Added regex-based chapter tagging in `ingest.py`.
- **Image Support (Multimodal)**:
    - *Technical*: Integrated `PyMuPDF` to extract images from PDFs.
    - *Frontend*: Chat now displays relevant images extracted from the retrieval context.

## [Phase 1.0] - 2025-12-30
### Initial Release
- **Core RAG Pipeline**: `ingest.py` (FAISS + OpenAI Embeddings) and `rag_qa.py` (ChatOpenAI + Context Retrieval).
- **Basic UI**: Streamlit application with a Chat Interface.
