from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import tempfile
import os

from rag.rag_pipeline import RAGPipeline
from llm.mock_llm import generate_mock_answer


app = FastAPI(
    title="DocuMind AI API",
    description="Document intelligence and RAG API",
    version="1.0.0"
)

rag = RAGPipeline()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "application": "DocuMind AI",
        "status": "running",
        "llm": "mock - Nexus pending"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp:

        contents = await file.read()
        temp.write(contents)
        temp_path = temp.name

    try:

        info = rag.load_document(temp_path)

        return {
            "message": "Document processed successfully",
            "pages": info["pages"],
            "tables": info["tables"],
            "images": info["images"],
            "ocr_pages": info["ocr_pages"],
            "chunks": info["chunks"],
            "multimodal_summary": info["multimodal_summary"]
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/ask")
def ask_question(request: QuestionRequest):

    if rag.vector_store is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a document first."
        )

    results = rag.search(
        request.question,
        top_k=3
    )

    answer = generate_mock_answer(
        request.question,
        results
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": [
            result["page"]
            for result in results
        ]
    }