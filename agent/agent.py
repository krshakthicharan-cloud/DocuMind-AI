from llm.mock_llm import generate_mock_answer


class DocuMindAgent:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline

    def run(self, question):
        question_lower = question.lower().strip()

        if not question_lower:
            return {
                "type": "error",
                "message": "Please enter a question."
            }

        # Decide what kind of task the user requested
        if any(
            word in question_lower
            for word in ["summarize", "summary", "overview"]
        ):
            action = "retrieve_summary"

        elif any(
            word in question_lower
            for word in ["page", "source", "where"]
        ):
            action = "retrieve_sources"

        else:
            action = "retrieve_answer"

        # Retrieve relevant document content
        results = self.rag.search(
            question,
            top_k=3
        )

        # Generate answer from retrieved content
        answer = generate_mock_answer(
            question,
            results
        )

        return {
            "type": action,
            "question": question,
            "answer": answer,
            "results": results,
            "result_count": len(results)
        }