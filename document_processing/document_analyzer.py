import os

try:
    import pymupdf as fitz
except ImportError:
    fitz = None


def analyze_document(file_path):
    """
    Analyze a PDF for pages, text, tables, and images.
    """

    if fitz is None:
        raise ImportError(
            "PyMuPDF is not installed. Run: pip install pymupdf"
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    doc = fitz.open(file_path)

    pages = []
    total_images = 0
    total_tables = 0

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text("text").strip()

        images = page.get_images(full=True)
        image_count = len(images)

        total_images += image_count

        table_count = 0

        try:
            finder = page.find_tables()

            if finder:
                table_count = len(finder.tables)

        except Exception:
            table_count = 0

        total_tables += table_count

        pages.append({
            "page": page_number,
            "text": text,
            "images": image_count,
            "tables": table_count
        })

    doc.close()

    return {
        "pages": len(pages),
        "images": total_images,
        "tables": total_tables,
        "page_data": pages
    }