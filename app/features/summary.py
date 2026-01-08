from langchain_core.prompts import ChatPromptTemplate
from app.services import llm
from app.retrieval import vectorstore

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful study assistant. partial text from a chapter is provided below.
Merge these points into a coherent, high-level summary of the chapter.
Start with: "In this chapter, we explore..."

Context:
{context}"""),
    ("human", "Summarize {topic}")
])

def summarize_chapter(chapter_name: str):
    """Summarizes a specific chapter by name."""
    if not vectorstore:
        return "⚠️ Vectorstore not initialized."
    
    print(f"📖 Summarizing: {chapter_name}")
    
    # Metadata filtering
    try:
        docs = vectorstore.similarity_search(
            "summary key concepts introduction conclusion", 
            k=8, 
            filter={"chapter": chapter_name}
        )
    except Exception as e:
        print(f"Filter error: {e}")
        docs = []

    # Fallback
    if not docs:
        print("⚠️ Filtering failed. Falling back to semantic search.")
        docs = vectorstore.similarity_search(f"Summary of {chapter_name}", k=8)

    if not docs:
        return f"❌ Could not find content for '{chapter_name}'. Try 'Chapter 1' or 'Introduction'."
        
    context = "\n\n".join([d.page_content for d in docs])
    
    chain = SUMMARIZE_PROMPT | llm
    res = chain.invoke({"context": context, "topic": chapter_name})
    
    return res.content
