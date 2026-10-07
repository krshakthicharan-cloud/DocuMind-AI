from rag.rag_pipeline import RAGPipeline
from llm.prompt_builder import build_prompt


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"

rag = RAGPipeline()

print("Loading document...")

info = rag.load_document(PDF_PATH)

print(
    f"Loaded {info['pages']} pages "
    f"and {info['chunks']} chunks."
)


question = "What is a stack?"

results = rag.search(
    question,
    top_k=3
)

prompt = build_prompt(
    question,
    results
)

print("\n========== GENERATED PROMPT ==========\n")
print(prompt)