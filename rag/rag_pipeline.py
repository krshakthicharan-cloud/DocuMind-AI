from document_processing.pdf_processor import extract_text_from_pdf
from document_processing.document_analyzer import analyze_document
from document_processing.ocr import extract_ocr_text
from document_processing.table_extractor import extract_tables_from_pdf
from document_processing.image_extractor import extract_images_from_pdf
from document_processing.multimodal_document import MultimodalDocument

from rag.chunker import create_chunks
from rag.embeddings import create_embeddings
from rag.vector_store import VectorStore


class RAGPipeline:

    def __init__(self):
        self.chunks = []
        self.vector_store = None
        self.document_info = None
        self.document = None

    def load_document(self, file_path):

        # --------------------------------
        # 1. Extract normal PDF text
        # --------------------------------

        pages = extract_text_from_pdf(file_path)

        # --------------------------------
        # 2. Analyze document
        # --------------------------------

        analysis = analyze_document(file_path)

        # --------------------------------
        # 3. OCR for scanned pages
        # --------------------------------

        ocr_pages = []

        try:
            ocr_pages = extract_ocr_text(file_path)
        except Exception:
            ocr_pages = []

        ocr_by_page = {
            item["page"]: item["text"]
            for item in ocr_pages
        }

        # Add OCR text when normal extraction
        # produced no text.

        for page in pages:

            page_number = page["page"]

            if (
                not page["text"].strip()
                and page_number in ocr_by_page
            ):
                page["text"] = ocr_by_page[page_number]

        # --------------------------------
        # 4. Detect and extract tables
        # --------------------------------

        try:
            tables = extract_tables_from_pdf(file_path)
        except Exception:
            tables = []

        # --------------------------------
        # 5. Extract embedded images
        # --------------------------------

        try:
            images = extract_images_from_pdf(file_path)
        except Exception:
            images = []

        # --------------------------------
        # 6. Create text chunks
        # --------------------------------

        self.chunks = create_chunks(pages)

        if not self.chunks:
            raise ValueError(
                "No text could be extracted from the document."
            )

        # --------------------------------
        # 7. Create embeddings
        # --------------------------------

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        embeddings = create_embeddings(texts)

        # --------------------------------
        # 8. Create vector store
        # --------------------------------

        self.vector_store = VectorStore(
            embeddings,
            self.chunks
        )

        # --------------------------------
        # 9. Create unified multimodal document
        # --------------------------------

        self.document = MultimodalDocument()

        self.document.add_pages(pages)
        self.document.add_tables(tables)
        self.document.add_images(images)
        self.document.add_ocr(ocr_pages)
        self.document.add_chunks(self.chunks)

        # --------------------------------
        # 10. Store document information
        # --------------------------------

        self.document_info = {
            "pages": len(pages),
            "tables": len(tables),
            "images": len(images),
            "ocr_pages": len(ocr_pages),
            "chunks": len(self.chunks),
            "multimodal_summary": self.document.summary()
        }

        return self.document_info

    def search(self, question, top_k=3):

        if self.vector_store is None:
            raise ValueError(
                "Please upload and process a document first."
            )

        question_embedding = create_embeddings(
            [question]
        )

        distances, indices = self.vector_store.search(
            question_embedding,
            top_k,
            query=question
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index < 0:
                continue

            if distance > 0.85:
                continue

            chunk = self.chunks[index]

            results.append({
                "text": chunk["text"],
                "page": chunk["page"],
                "distance": float(distance)
            })

        return results