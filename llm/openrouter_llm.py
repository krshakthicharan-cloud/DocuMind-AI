
import os
from openai import OpenAI


def generate_answer(question, retrieved_chunks):
    if not retrieved_chunks:
        return "I couldn't find relevant information in the uploaded document."

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    context = "\n\n".join(
        f"[Page {chunk['page']}]\n{chunk['text']}"
        for chunk in retrieved_chunks
    )

    response = client.chat.completions.create(
        model="amazon/nova-micro-v1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are DocuMind AI, a PDF question-answering assistant. "
                    "Answer using only the supplied document context. "
                    "Do not invent facts. If the answer is absent, say so. "
                    "Include relevant page numbers."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Document context:\n{context}"
                ),
            },
        ],
    )

    return response.choices[0].message.content or (
        "I couldn't generate an answer."
    )
