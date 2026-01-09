import time
import sys
# Force UTF-8 for Windows terminals/pipes
sys.stdout.reconfigure(encoding='utf-8')

from app.retrieval import retriever
from app.rag_qa import conversational_chain
from app.evaluation import evaluate_rag_response

# Test Dataset
TEST_CASES = [
    "What is BERT?",
    "Explain the attention mechanism.",
    "What is the GLUE benchmark?",
    "Who are the authors of the Attention paper?", # Specific fact
    "How do I cook a pancake?" # Out of domain
]

def run_evaluation():
    print("⚖️  Running LLM-as-a-Judge Evaluation...\n")
    
    results = []
    
    for query in TEST_CASES:
        print(f"🔹 Query: '{query}'")
        
        # 1. Run RAG
        # We need to manually invoke retrieval to get context for the judge
        docs = retriever.invoke(query)
        context_text = "\n\n".join([d.page_content for d in docs])
        
        # Invoke Chain
        response = conversational_chain.invoke(
            {"input": query}, 
            config={"configurable": {"session_id": "eval_session"}}
        )
        answer = response["answer"]
        
        # 2. Evaluate
        print("   Thinking (Judging)...")
        eval_result = evaluate_rag_response(query, context_text, answer)
        
        # 3. Report
        score = eval_result.get("score", 0)
        print(f"   📝 Score: {score}/5")
        print(f"   💡 Reason: {eval_result.get('reasoning')}")
        print("-" * 50)
        
        results.append(score)

    avg_score = sum(results) / len(results)
    print(f"\n🏆 Average Quality Score: {avg_score:.2f}/5")

if __name__ == "__main__":
    run_evaluation()
