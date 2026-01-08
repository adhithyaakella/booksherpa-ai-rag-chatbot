# Phase 4: Advanced RAG Implementation Log 🧠

This document tracks the technical details, configuration, and impact of Advanced RAG features implemented in BookSherpa AI.

## 📊 Evaluation Metrics
| Metric | Baseline (Dense) | Hybrid (BM25+FAISS) | Hybrid + Re-rank |
| :--- | :--- | :--- | :--- |
| **Recall@5** | **25.0%** | **25.0%** (Metric limited by synonyms) | TBD |

**Analysis**:
-   **Hybrid Search**: Successfully retrieved *relevant* docs for "GLUE" (benchmark contexts) but missed the specific definition chunk.
-   **Missed Matches**: "Cross-attention" appeared as "Encoder-Decoder attention" (Synonym issue).
-   **Solution**: Re-ranking is now ACTIVE. Latency increased from ~0.17s to ~0.64s, confirming the Cross-Encoder model is processing the Top 20 candidates.

## 1. Hybrid Search (Keyword + Semantic)
**Status**: ✅ **Implemented**
**Configuration**:
-   Weights: 0.5 (Dense) / 0.5 (Sparse).
-   Retrievers: FAISS (k=10) + BM25 (k=10).
-   Total Candidates: 20 (before re-ranking).

## 2. Cross-Encoder Re-ranking
**Status**: ✅ **Implemented**
**Configuration**:
-   Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
-   Input: Top 20 Candidates (from Hybrid).
-   Output: Top 5 Re-ranked Documents.
**Impact**:
-   Ensures that even if BM25 finds a keyword match at rank #15, the Re-ranker can pull it to #1 if it answers the question.
**Goal**: Solve the "Specific Acronym/Term" blindness of pure vector search.
**Strategy**:
-   **Component**: `EnsembleRetriever` (LangChain).
-   **Retrievers**:
    1.  `FAISS` (Dense Vector Search) - Weight: 0.5
    2.  `BM25Retriever` (Sparse Keyword Search) - Weight: 0.5
-   **Implementation Details**:
    -   Need to install `rank_bm25`.
    -   BM25 index must be built from the *same* chunks as FAISS.
    -   `create_retrieval_chain` will use the Ensemble instead of just FAISS.

## 2. Cross-Encoder Re-ranking
**Status**: ⏳ Pending
**Goal**: Improve precision of the "Top N" context fed to the LLM.
**Strategy**:
-   **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (HuggingFace).
-   **Workflow**:
    1.  Fetch Top 20 documents (Hybrid or Dense).
    2.  Pass (Query, Doc) pairs to Cross-Encoder.
    3.  Select Top 5 highest scores.
-   **Impact**:
    -   Filters out "distractor" documents that are semantically close but factually irrelevant.

## 3. Query Expansion (Multi-Query)
**Status**: ⏳ Pending
**Goal**: Handle ambiguous or simple user queries better.
**Strategy**:
-   Use LLM to generate 3 variations of the user's question.
-   Retrieve documents for *all* variations.
-   Deduplicate results.

---
*Log will be updated as features are deployed.*
