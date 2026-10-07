import os
import unittest

from document_processing.pdf_processor import extract_text_from_pdf
from document_processing.document_analyzer import analyze_document
from document_processing.ocr import is_ocr_available
from rag.rag_pipeline import RAGPipeline
from agent.agent import DocuMindAgent


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"

class TestDocuMindAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(PDF_PATH):
            raise FileNotFoundError(
                f"PDF not found: {PDF_PATH}"
            )

        cls.rag = RAGPipeline()
        cls.info = cls.rag.load_document(PDF_PATH)

    def test_pdf_extraction(self):
        pages = extract_text_from_pdf(PDF_PATH)

        self.assertGreater(
            len(pages),
            0
        )

    def test_document_analysis(self):
        info = analyze_document(PDF_PATH)

        self.assertGreater(
            info["pages"],
            0
        )

        self.assertGreaterEqual(
            info["tables"],
            0
        )

        self.assertGreaterEqual(
            info["images"],
            0
        )

    def test_ocr_available(self):
        self.assertTrue(
            is_ocr_available()
        )

    def test_multimodal_document(self):
        self.assertIsNotNone(
            self.rag.document
        )

        self.assertGreater(
            self.info["pages"],
            0
        )

        self.assertGreater(
            self.info["chunks"],
            0
        )

    def test_rag_search(self):
        results = self.rag.search(
            "What is a stack?",
            top_k=3
        )

        self.assertGreater(
            len(results),
            0
        )

    def test_agent(self):
        agent = DocuMindAgent(
            self.rag
        )

        result = agent.run(
            "What is a stack?"
        )

        self.assertIn(
            "results",
            result
        )

        self.assertGreaterEqual(
            result["result_count"],
            0
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)