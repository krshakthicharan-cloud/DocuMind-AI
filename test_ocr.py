from document_processing.ocr import extract_ocr_text


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"

print("Running OCR...")

results = extract_ocr_text(PDF_PATH)

print(f"\nOCR returned {len(results)} pages.")

for result in results:

    print("\n" + "=" * 60)

    print(f"Page: {result['page']}")

    print("=" * 60)

    print(result["text"][:1000])