# Changelog & Update History 📜

All notable changes to the **BookSherpa AI** project will be documented in this file.

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
