import os
import sys
import uuid
import glob
from dotenv import load_dotenv

import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

import spacy

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- Config ---
load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "data/NLP_with_Transformers_Oreilly.pdf")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "vectorstore/db_faiss")
SPACY_MODEL = "en_core_web_sm"

# --- spaCy Model Check/Download ---
try:
    nlp = spacy.load(SPACY_MODEL)
except OSError:
    import spacy.cli

    spacy.cli.download(SPACY_MODEL)
    nlp = spacy.load(SPACY_MODEL)


# --- Helper: Check if FAISS index exists ---
def faiss_index_exists(path):
    files = glob.glob(os.path.join(path, "index.*"))
    return bool(files)


# --- Step 1: Load PDF ---
def load_pdf(pdf_path):
    loader = UnstructuredPDFLoader(pdf_path)
    return loader.load()


# --- Step 2: Chunk documents ---
def chunk_docs(documents, chunk_size=500, chunk_overlap=75):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)


# --- Step 3: Enrich with spaCy NER ---
def enrich_with_spacy(docs):
    enriched = []
    for doc in docs:
        spacy_doc = nlp(doc.page_content)
        ents = [f"{ent.label_}:{ent.text}" for ent in spacy_doc.ents]
        doc.metadata["named_entities"] = ents
        doc.metadata["chunk_id"] = str(uuid.uuid4())
        enriched.append(doc)
    return enriched


# --- Step 4: Embed & Store ---
def embed_and_store(docs):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(VECTOR_DB_DIR)
    print(f"✅ Vector DB saved at: {VECTOR_DB_DIR}")


# --- Main Flow ---
def main(force=False):
    if (
        not force
        and os.path.exists(VECTOR_DB_DIR)
        and faiss_index_exists(VECTOR_DB_DIR)
    ):
        print(f"⚠️ Vector DB already exists at '{VECTOR_DB_DIR}'. Skipping ingestion.")
        print("👉 Use '--force' to reprocess and overwrite existing embeddings.\n")
        return

    print("📄 Loading document...")
    raw_docs = load_pdf(PDF_PATH)

    print("✂️ Chunking...")
    chunks = chunk_docs(raw_docs)
    print(f"✅ Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i+1} ---\n{chunk.page_content[:400]}...")

    print("🧠 Enriching with spaCy NER...")
    enriched_chunks = enrich_with_spacy(chunks)

    print("📦 Embedding and storing in vector DB...")
    embed_and_store(enriched_chunks)

    print("🎉 Done.")


# --- Entry Point ---
if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    main(force=force_flag)
