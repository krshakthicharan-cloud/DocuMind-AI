from document_processing.pdf_processor import extract_text_from_pdf


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"

pages = extract_text_from_pdf(PDF_PATH)

for page in pages:

    if page["page"] in [3, 6, 8, 10, 12, 13, 15]:

        print(
            f"\n========== PAGE {page['page']} ==========\n"
        )

        print(page["text"])