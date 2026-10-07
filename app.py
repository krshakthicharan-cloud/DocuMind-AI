import gradio as gr

from rag.rag_pipeline import RAGPipeline
from agent.agent import DocuMindAgent
from llm.mock_llm import generate_mock_answer


# -----------------------------
# Initialize application
# -----------------------------

rag = RAGPipeline()
agent = DocuMindAgent(rag)


# -----------------------------
# Process document
# -----------------------------

def process_document(file):
    if file is None:
        return "Please upload a PDF first."

    try:
        info = rag.load_document(file)

        ocr_status = (
            "Available"
            if info["ocr_pages"] > 0
            else "Not detected"
        )

        return (
            "Document processed successfully!\n\n"
            f"Pages: {info['pages']}\n"
            f"Text chunks: {info['chunks']}\n"
            f"Tables detected: {info['tables']}\n"
            f"Images detected: {info['images']}\n"
            f"OCR pages: {info['ocr_pages']}\n"
            f"OCR status: {ocr_status}"
        )

    except Exception as e:
        return "Error processing document:\n" + str(e)


# -----------------------------
# Answer question
# -----------------------------

def answer_question(question):

    if not question.strip():
        return (
            "Please enter a question.",
            ""
        )

    try:
        agent_result = agent.run(question)

        results = agent_result["results"]

        answer = generate_mock_answer(
            question,
            results
        )

        sources = []

        for result in results:
            page = result["page"]

            if page not in sources:
                sources.append(page)

        if sources:
            source_text = (
                "Sources: "
                + ", ".join(
                    f"Page {page}"
                    for page in sources
                )
            )
        else:
            source_text = "Sources: None"

        return answer, source_text

    except Exception as e:
        return (
            f"Error:\n{str(e)}",
            ""
        )


# -----------------------------
# Gradio interface
# -----------------------------

with gr.Blocks(
    title="DocuMind AI"
) as demo:

    gr.Markdown(
        """
        # DocuMind AI

        ### Multimodal Document Intelligence

        Upload a PDF, process it, and ask questions
        about its content using Retrieval-Augmented
        Generation (RAG).
        """
    )

    gr.Markdown("## Document Processing")

    document = gr.File(
        label="Upload PDF",
        file_types=[".pdf"],
        type="filepath"
    )

    process_button = gr.Button(
        "Process Document",
        variant="primary"
    )

    status = gr.Textbox(
        label="Document Analysis",
        lines=7
    )

    process_button.click(
        fn=process_document,
        inputs=document,
        outputs=status
    )

    gr.Markdown("## Ask DocuMind")

    question = gr.Textbox(
        label="Your Question",
        placeholder="Example: What is a stack?",
        lines=2
    )

    ask_button = gr.Button(
        "Ask DocuMind",
        variant="primary"
    )

    answer = gr.Textbox(
        label="Answer",
        lines=10
    )

    sources = gr.Textbox(
        label="Sources",
        lines=2
    )

    ask_button.click(
        fn=answer_question,
        inputs=question,
        outputs=[answer, sources]
    )

    gr.Markdown(
        """
        ---

        ### System Architecture

        **PDF → Document Analyzer → OCR → Chunking → RAG → Agent → Answer + Sources**

        ### LLM Status

        The current application uses a temporary local mock LLM.

        **Nexus AI integration is pending until the required
        API credentials, endpoint, model, and authentication
        information are provided.**
        """
    )


# -----------------------------
# Start application
# -----------------------------

if __name__ == "__main__":
    demo.launch()