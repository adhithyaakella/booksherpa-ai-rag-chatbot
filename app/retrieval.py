from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors.cross_encoder import BaseCrossEncoder

from app.config import VECTORSTORE_PATH
from langchain.retrievers.multi_query import MultiQueryRetriever
from app.services import embedding_model, llm

# --- Adapter for Pydantic Compatibility ---
class HFCrossEncoderAdapter(BaseCrossEncoder):
    model: HuggingFaceCrossEncoder = None

    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self, model: HuggingFaceCrossEncoder):
        super().__init__()
        self.model = model

    def score(self, text_pairs: List[Tuple[str, str]]) -> List[float]:
        return self.model.score(text_pairs)

# --- Initialize Vector Store & Retriever ---
vectorstore = None
retriever = None

def initialize():
    global vectorstore, retriever
    
    # 1. Load Vectorstore
    try:
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH, embedding_model, allow_dangerous_deserialization=True
        )
    except RuntimeError:
        print(f"⚠️ Vectorstore not found at {VECTORSTORE_PATH}. Run ingest.py first.")
        vectorstore = None
        retriever = None
        return

    # 2. Build Base Retriever
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    
    # 3. Hybrid Search (BM25)
    try:
        all_docs = list(vectorstore.docstore._dict.values())
        bm25_retriever = BM25Retriever.from_documents(all_docs)
        bm25_retriever.k = 10
        
        hybrid_retriever = EnsembleRetriever(
            retrievers=[faiss_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )
    except Exception as e:
        print(f"⚠️ Hybrid Search Init Failed: {e}")
        hybrid_retriever = faiss_retriever
        
    # 3.5. Query Expansion (Multi-Query)
    # Uses LLM to generate 3 variations of the question
    try:
        print("🧠 Initializing Query Expansion...")
        base_retriever = MultiQueryRetriever.from_llm(
            retriever=hybrid_retriever,
            llm=llm
        )
    except Exception as e:
        print(f"⚠️ Query Expansion Init Failed: {e}")
        base_retriever = hybrid_retriever

    # 4. Re-Ranking
    try:
        model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        community_encoder = HuggingFaceCrossEncoder(model_name=model_name)
        adapter = HFCrossEncoderAdapter(model=community_encoder)
        compressor = CrossEncoderReranker(model=adapter, top_n=5)
        
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )
    except Exception as e:
        print(f"❌ Re-ranker Init Failed: {e}")
        retriever = base_retriever

# Initial load
initialize()

def get_retriever():
    """Returns the global retriever, initializing if needed."""
    if not retriever:
        initialize()
    return retriever

def reload_retriever():
    """Forces a reload of the vectorstore from disk."""
    print("♻️ Reloading Retriever from disk...")
    initialize()
    return retriever
