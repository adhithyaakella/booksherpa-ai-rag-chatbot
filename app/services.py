from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import OPENAI_API_KEY

# --- Initialize Components ---

# 1. Embeddings
# Used for both Ingestion and Retrieval
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 2. Main LLM (OpenAI)
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY, 
    model_name="gpt-4o-mini",
    temperature=0.7
)
