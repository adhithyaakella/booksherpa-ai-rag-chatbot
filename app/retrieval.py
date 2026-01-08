from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors.cross_encoder import BaseCrossEncoder

from app.config import VECTORSTORE_PATH
from app.services import embedding_model

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

# --- Initialize Vector Store ---
try:
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH, embedding_model, allow_dangerous_deserialization=True
    )
except RuntimeError:
    print(f"⚠️ Vectorstore not found at {VECTORSTORE_PATH}. Run ingest.py first.")
    vectorstore = None

# --- Build Advanced Retriever ---
def get_retriever():
    if not vectorstore:
        return None
        
    # 1. Base Dense Retriever
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    
    # 2. Add Sparse Retriever (Hybrid)
    try:
        all_docs = list(vectorstore.docstore._dict.values())
        bm25_retriever = BM25Retriever.from_documents(all_docs)
        bm25_retriever.k = 10
        
        base_retriever = EnsembleRetriever(
            retrievers=[faiss_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )
    except Exception as e:
        print(f"⚠️ Hybrid Search Init Failed: {e}")
        base_retriever = faiss_retriever

    # 3. Add Re-Ranking (Cross-Encoder)
    try:
        model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        community_encoder = HuggingFaceCrossEncoder(model_name=model_name)
        adapter = HFCrossEncoderAdapter(model=community_encoder)
        compressor = CrossEncoderReranker(model=adapter, top_n=5)
        
        final_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )
        return final_retriever
    except Exception as e:
        print(f"❌ Re-ranker Init Failed: {e}")
        return base_retriever

# Global Singleton for import
retriever = get_retriever()
