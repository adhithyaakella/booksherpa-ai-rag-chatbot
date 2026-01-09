import os
import sys
import uuid
import glob
import warnings
import spacy

import spacy

# Re-add project root to sys.path so we can import from 'app'
# This fixes ModuleNotFoundError when running 'python app/ingest.py' directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force UTF-8 for Windows terminals/pipes to support emojis
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Modular Imports
from app.config import VECTORSTORE_PATH, PROJECT_ROOT
from app.services import embedding_model

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

# --- Config ---
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SPACY_MODEL = "en_core_web_sm"

# --- spaCy Model Check/Download ---
try:
    nlp = spacy.load(SPACY_MODEL)
except OSError:
    print(f"Downloading spaCy model '{SPACY_MODEL}'...")
    import spacy.cli
    spacy.cli.download(SPACY_MODEL)
    nlp = spacy.load(SPACY_MODEL)


# --- Helper: Check if FAISS index exists ---
def faiss_index_exists(path):
    files = glob.glob(os.path.join(path, "index.*"))
    return bool(files)


# --- Step 1: Load Documents ---
def load_documents(data_dir):
    docs = []
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found.")
        return []

    # Map ext to loader
    loaders = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader
    }

    print(f"📂 Scanning '{data_dir}' for documents...")
    
    count = 0
    # Use glob to recursively find files
    for root, dir, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            if ext in loaders:
                print(f"   - Found: {file}")
                try:
                    loader_cls = loaders[ext]
                    loader = loader_cls(file_path)
                    file_docs = loader.load()
                    docs.extend(file_docs)
                    count += 1
                    print(f"     ✅ Loaded ({len(file_docs)} pages/docs)")
                except Exception as e:
                    print(f"     ❌ Failed to load: {e}")
                    
    if count == 0:
        print("   ⚠️ No matching files found (looking for .pdf, .txt, .md)")
        
    return docs


# --- Step 2: Chunk documents ---
def chunk_docs(documents, chunk_size=1200, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(documents)
    return enrich_metadata(chunks)

def enrich_metadata(chunks):
    """Tags chunks with Chapter headers based on simple regex."""
    import re
    chapter_regex = re.compile(r"(?:^|\n)(Chapter\s+\d+|PART\s+[IVX]+|[0-9]+\.\s+[A-Z][a-z]+)", re.IGNORECASE)
    
    current_chapter = "General / Introduction"
    
    for doc in chunks:
        # Search for chapter header in the first 200 chars of the chunk
        content_sample = doc.page_content[:200]
        match = chapter_regex.search(content_sample)
        if match:
            current_chapter = match.group(1).strip()
            
        doc.metadata["chapter"] = current_chapter
        
    return chunks


# --- Step 3: Enrich with spaCy NER ---
def enrich_with_spacy(docs):
    enriched = []
    print(f"🧠 Enriching {len(docs)} chunks with NER (this may take a while)...")
    for i, doc in enumerate(docs):
        # Basic progress indicator
        if i % 50 == 0: print(".", end="", flush=True)
        
        if not doc.page_content:
            continue
            
        # Clean text to remove surrogates that crash spacy and transformers
        try:
            # Ensure it's a string
            text_content = str(doc.page_content)
            # Remove surrogates
            clean_text = text_content.encode("utf-8", "ignore").decode("utf-8")
            # Update the doc object so the embedding model gets the clean text too
            doc.page_content = clean_text
        except Exception:
            clean_text = ""
            
        if not clean_text.strip():
            continue

        spacy_doc = nlp(clean_text)
        ents = [f"{ent.label_}:{ent.text}" for ent in spacy_doc.ents]
        doc.metadata["named_entities"] = ents
        doc.metadata["chunk_id"] = str(uuid.uuid4())
        enriched.append(doc)
    print("\n")
    return enriched


# --- Step 4: Image Extraction (Multimodal) ---
def extract_images_from_pdf(pdf_path, output_dir_relative="frontend/static/images"):
    import fitz # PyMuPDF
    
    # Ensure output dir exists (absolute)
    output_abs = os.path.abspath(output_dir_relative)
    os.makedirs(output_abs, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    filename = os.path.basename(pdf_path)
    safe_name = os.path.splitext(filename)[0]
    
    images_found = {} # (page_idx) -> relative_path
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                
                if pix.width < 150 or pix.height < 150:
                    continue # Skip small icons
                    
                image_filename = f"{safe_name}_p{page_index}.png"
                
                # IMPORTANT: Streamlit runs from PROJECT_ROOT.
                # So the path must be relative to PROJECT_ROOT, i.e., "frontend/static/images/..."
                image_rel_path = f"frontend/static/images/{image_filename}" 
                
                # Actual save location
                save_path = os.path.join(output_abs, image_filename)
                
                if pix.n - pix.alpha < 4:
                    pix.save(save_path)
                else:
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.save(save_path)
                    pix1 = None
                pix = None
                
                images_found[page_index] = image_rel_path
                break 
            except Exception as e:
                # print(f"   ⚠️ Image extract error on p{page_index}: {e}")
                continue
            
    return images_found


# --- Step 5: Link Images to Chunks ---
def link_images_to_chunks(chunks, image_map):
    """
    image_map: { (filename, page_num): image_path }
    """
    for doc in chunks:
        source = doc.metadata.get("source", "")
        page = doc.metadata.get("page", -1)
        filename = os.path.basename(source)
        
        key = (filename, page)
        if key in image_map:
            doc.metadata["image_path"] = image_map[key]
            
    return chunks


# --- Step 6: Embed & Store ---
def embed_and_store(docs):
    if not docs:
        print("⚠️ No documents to embed.")
        return
        
    print("📦 Embedding and indexing...")
    # Use the shared model from app.services
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"✅ Vector DB saved at: {VECTORSTORE_PATH}")


# --- Main Flow ---
def main(force=False):
    if (
        not force
        and os.path.exists(VECTORSTORE_PATH)
        and faiss_index_exists(VECTORSTORE_PATH)
    ):
        print(f"⚠️ Vector DB already exists at '{VECTORSTORE_PATH}'.")
        print("👉 Use '--force' to rebuild the index from scratch.")
        return

    # 1. Load Text
    raw_docs = load_documents(DATA_DIR)
    
    if not raw_docs:
        print("❌ No documents found to ingest.")
        return

    # 2. Extract Images (Pre-processing)
    print("🖼️  Extracting images from PDFs...")
    global_image_map = {} # (filename, page) -> path
    
    pdf_sources = set([d.metadata["source"] for d in raw_docs if d.metadata["source"].endswith(".pdf")])
    
    for pdf_path in pdf_sources:
        try:
            page_map = extract_images_from_pdf(pdf_path)
            filename = os.path.basename(pdf_path)
            for page, path in page_map.items():
                global_image_map[(filename, page)] = path
        except Exception as e:
            print(f"   ❌ Image extraction failed for {pdf_path}: {e}")

    # 3. Chunk
    chunks = chunk_docs(raw_docs)
    print(f"✅ Created {len(chunks)} chunks.")

    # 4. Link Images
    chunks = link_images_to_chunks(chunks, global_image_map)

    # 5. Enrich (NER)
    enriched_chunks = enrich_with_spacy(chunks)

    # 6. Store
    embed_and_store(enriched_chunks)
    print("🎉 Ingestion Complete.")


# --- Entry Point ---
if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    main(force=force_flag)
