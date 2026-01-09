import json
import re
from langchain_core.prompts import ChatPromptTemplate
from app.services import llm
from app.retrieval import vectorstore

QUIZ_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an educational assistant. Generate 10 multiple-choice questions based on the context provided.
You must return the output as a valid JSON list of objects. Do not wrap in markdown code blocks.
Each object must have:
- "question": str
- "options": [str, str, str, str] (4 options)
- "answer": str (Must match one of the options exactly)
- "explanation": str (Short explanation of why it is correct)

Context:
{context}"""),
    ("human", "Generate a quiz about: {topic}")
])

def generate_quiz(topic: str):
    """Generates 10 quiz questions in JSON format."""
    if not vectorstore:
        return []

    print(f"🎓 Generating JSON quiz for: {topic}")

    # Broad search for context
    docs = vectorstore.similarity_search(topic, k=10)
    if not docs:
        return []
        
    context = "\n\n".join([d.page_content for d in docs])
    
    chain = QUIZ_PROMPT | llm
    res = chain.invoke({"context": context, "topic": topic})
    content = res.content.strip()
    
    # Clean Markdown
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
        
    try:
        data = json.loads(content.strip())
        return data
    except json.JSONDecodeError:
        print("❌ Failed to decode Quiz JSON")
        return []
