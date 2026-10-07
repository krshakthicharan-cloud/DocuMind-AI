from rag.rag_pipeline import RAGPipeline
from llm.mock_llm import generate_mock_answer


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"

rag = RAGPipeline()

print("Loading document...")

info = rag.load_document(PDF_PATH)

print(
    f"Loaded {info['pages']} pages "
    f"and {info['chunks']} chunks."
)

question = input("\nAsk a question: ")

print("\nSearching document...")

results = rag.search(
    question,
    top_k=3
)

print("\nGenerating answer...")

answer = generate_mock_answer(
    question,
    results
)

print("\n========== DOCUMIND AI ANSWER ==========\n")

print(answer)

print("\n========================================")