SYSTEM_PROMPT = """
You are DocuMind AI, a document understanding assistant.

Your job is to answer questions using ONLY the provided document context.

Rules:
1. Use only information found in the provided context.
2. Do not invent or assume information.
3. If the answer cannot be found in the context, say:
   "The information is not available in the uploaded document."
4. Give a clear and concise answer.
5. Include the relevant page numbers.
6. If multiple pages are relevant, mention all of them.
"""


def build_prompt(question, retrieved_results):

    context_parts = []

    for result in retrieved_results:

        context_parts.append(
            f"[Page {result['page']}]\n"
            f"{result['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
{SYSTEM_PROMPT}

DOCUMENT CONTEXT:
-----------------
{context}
-----------------

USER QUESTION:
{question}

ANSWER:
"""

    return prompt