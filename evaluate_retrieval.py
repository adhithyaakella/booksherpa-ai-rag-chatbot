import time
from app.retrieval import vectorstore, retriever
from langchain_core.documents import Document
import sys

# Force UTF-8 for Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

# 1. Golden Dataset: Questions where we expect specific answers
# (We assume ground truth based on manual verification or naive checks)
# For a real metric, we'd need labeled (Question, ChunkID) pairs.
# Here, we will use "Proxy Metrics": Does the retrieval contain key terms?

TEST_CASES = [
    {
        "query": "What is BERT?",
        "expected_terms": ["Bidirectional Encoder Representations", "Transformer"],
        "difficulty": "Medium"
    },
    {
        "query": "attention mechanism",
        "expected_terms": ["Query", "Key", "Value", "weights"],
        "difficulty": "Easy"
    },
    {
        "query": "GLUE benchmark",
        "expected_terms": ["GLUE", "General Language Understanding Evaluation"],
        "difficulty": "Hard (Acronym)"
    },
    {
        "query": "What is the difference between specific attention types?",
        "expected_terms": ["self-attention", "cross-attention"],
        "difficulty": "Hard (Concept)"
    }
]

def evaluate_baseline():
    output_lines = []
    output_lines.append(f"Evaluating Hybrid Retrieval ({len(TEST_CASES)} queries)...")
    
    total_score = 0
    start_global = time.time()
    
    for case in TEST_CASES:
        q = case["query"]
        terms = case["expected_terms"]
        
        output_lines.append(f"\nQuery: '{q}'")
        
        start_t = time.time()
        # USE THE HYBRID RETRIEVER
        if retriever:
             docs = retriever.invoke(q)
        else:
             docs = []
             output_lines.append("  [darn] Retriever is None")
             
        duration = time.time() - start_t
        
        # 2. Check for terms
        found_terms = 0
        context_text = " ".join([d.page_content for d in docs])
        
        passed = True
        missing = []
        for t in terms:
            if t.lower() not in context_text.lower():
                passed = False
                missing.append(t)
        
        if passed:
            output_lines.append(f"  [PASS] ({duration:.2f}s)")
            total_score += 1
        else:
            output_lines.append(f"  [FAIL] ({duration:.2f}s)")
            output_lines.append(f"     Missing: {missing}")
            # Clean newlines for readability
            clean_context = context_text.replace("\n", " ")[:600]
            output_lines.append(f"     Retrieved: {clean_context}...")

    accuracy = (total_score / len(TEST_CASES)) * 100
    output_lines.append(f"\nBaseline Accuracy: {accuracy:.1f}%")
    output_lines.append(f"Total Time: {time.time() - start_global:.2f}s")
    
    # Write to file
    with open("eval_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    # Print simple
    print("\n".join(output_lines))

if __name__ == "__main__":
    if not vectorstore:
        print("❌ FAISS Index not found.")
    else:
        evaluate_baseline()
