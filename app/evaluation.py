from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services import llm

# --- Prompts ---

EVAL_PROMPT = ChatPromptTemplate.from_template("""
You are an expert grader for a RAG (Retrieval Augmented Generation) system.
Your task is to evaluate the quality of a generated Answer based on the User Query and the Retrieved Context.

User Query: {query}
Retrieved Context: {context}
Generated Answer: {answer}

Criteria:
1. **Faithfulness**: Is the answer derived entirely from the provided context? (If context is empty, answer should admit ignorance).
2. **Relevance**: Does the answer directly address the user's query?
3. **Accuracy**: Does the answer seem correct based on the context?

Output your evaluation as a JSON object with:
- "score": A score from 1 to 5 (5 being perfect).
- "reasoning": A brief explanation of the score.
- "metric": "Overall Quality"

JSON Output:
""")

def evaluate_rag_response(query, context_text, answer):
    """
    Uses the LLM to grade the RAG response.
    Returns: dict {score, reasoning}
    """
    try:
        chain = EVAL_PROMPT | llm | JsonOutputParser()
        result = chain.invoke({
            "query": query,
            "context": context_text,
            "answer": answer
        })
        return result
    except Exception as e:
        return {"score": 0, "reasoning": f"Evaluation Failed: {e}"}
