
import os
from openai import OpenAI


def generate_answer(question, retrieved_chunks):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    if not retrieved_chunks:
        return (
            "I couldn't find relevant information "
            "in the uploaded document."
        )

    client = OpenAI(api_key=api_key)

    context = "\n\n".join(
        f"[Page {chunk['page']}]\n{chunk['text']}"
        for chunk in retrieved_chunks
    )

    response = client.responses.create(
        model=os.getenv(
            "OPENAI_MODEL",
            "gpt-4.1-nano"
        ),
        instructions=(
            "You are DocuMind AI, a PDF question-answering "
            "assistant. Answer using only the supplied "
            "document context. Do not invent facts. "
            "If the answer is not in the context, say so. "
            "Include the relevant page numbers in your answer."
        ),
        input=(
            f"Question:\n{question}\n\n"
            f"Document context:\n{context}"
        )
    )

    return response.output_text
