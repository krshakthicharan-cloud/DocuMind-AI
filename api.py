
import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.rag_pipeline import RAGPipeline
from llm.openrouter_llm import generate_answer


# Initialize FastAPI first.
app = FastAPI(
    title="DocuMind AI API",
    description="Document intelligence and RAG API",
    version="1.0.0",
)

# Allow requests from the local frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the existing RAG pipeline.
rag = RAGPipeline()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "application": "DocuMind AI",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "DocuMind AI",
        "document_loaded": rag.vector_store is not None,
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    temp_path = None

    try:
        # Save the uploaded PDF temporarily.
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp:
            temp.write(contents)
            temp_path = temp.name

        # Use the project's existing document-processing pipeline.
        info = rag.load_document(temp_path)

        return {
            "status": "success",
            "message": "Document processed successfully",
            "filename": file.filename,
            "pages": info.get("pages", 0),
            "tables": info.get("tables", 0),
            "images": info.get("images", 0),
            "ocr_pages": info.get("ocr_pages", 0),
            "chunks": info.get("chunks", 0),
            "multimodal_summary": info.get("multimodal_summary", ""),
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Document processing error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check the backend terminal.",
        ) from exc

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    if rag.vector_store is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a document first.",
        )

    try:
        # Retrieve relevant document chunks using the existing RAG pipeline.
        results = rag.search(
            question,
            top_k=3,
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No relevant document content was found.",
            )

        # Generate an answer using the existing LLM integration.
        answer = generate_answer(question, results)

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty answer.",
            )

        # Keep source information compatible with the frontend.
        sources = list(
            dict.fromkeys(
                result["page"]
                for result in results
                if result.get("page") is not None
            )
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Question answering error: {exc}")
        raise HTTPException(
            status_code=502,
            detail=(
                "AI answer generation failed. "
                "Check your OpenRouter configuration and backend terminal."
            ),
        ) from exc
