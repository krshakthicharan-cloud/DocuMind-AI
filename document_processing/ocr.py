import shutil


def is_ocr_available():
    return shutil.which("tesseract") is not None


def extract_ocr_text(file_path):
    """
    Optional OCR extraction for scanned PDFs.

    Requires:
    - pymupdf
    - pytesseract
    - Tesseract OCR installed on the system
    """

    if not is_ocr_available():
        return []

    import pymupdf as fitz
    import pytesseract
    from PIL import Image
    import io

    doc = fitz.open(file_path)

    results = []

    for page_number, page in enumerate(doc, start=1):

        pix = page.get_pixmap(
            matrix=fitz.Matrix(1.5, 1.5)
        )

        image = Image.open(
            io.BytesIO(pix.tobytes("png"))
        )

        text = pytesseract.image_to_string(
            image
        ).strip()

        if text:
            results.append({
                "page": page_number,
                "text": text
            })

    doc.close()

    return results