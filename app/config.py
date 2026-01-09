import warnings
# Suppress the pkg_resources deprecation warning (common in older libs)
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# --- Config & Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORSTORE_PATH = os.path.join(PROJECT_ROOT, "vectorstore", "db_faiss")
DB_PATH = os.path.join(PROJECT_ROOT, "chat_history.db")
SQL_CONNECTION_STR = f"sqlite:///{DB_PATH}"

# --- Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_config():
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY not found in .env. Please add it to continue.")
    
# Initialize on import
validate_config()
