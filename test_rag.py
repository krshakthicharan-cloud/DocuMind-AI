from rag.rag_pipeline import RAGPipeline

PDF_PATH =r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"
rag = RAGPipeline()

print("Loading document...")
info = rag.load_document(PDF_PATH)

print("\nDocument information:")
print(info)

print("\nMultimodal summary:")
print(rag.document.summary())

print("\nTesting search...")
results = rag.search("What is a stack?", top_k=3)

for result in results:
    print("\nPage:", result["page"])
    print("Distance:", result["distance"])
    print("Text:", result["text"][:300])