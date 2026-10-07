from document_processing.table_extractor import (
    extract_tables_from_pdf,
    tables_to_text
)


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"


print("Extracting tables...")

tables = extract_tables_from_pdf(
    PDF_PATH
)

print(
    f"\nFound {len(tables)} tables."
)

for table in tables:

    print(
        f"\n========== "
        f"TABLE {table['table']} "
        f"PAGE {table['page']} "
        f"=========="
    )

    print(table["text"])


print(
    "\n========== SEARCHABLE TABLE TEXT ==========\n"
)

text_blocks = tables_to_text(tables)

for block in text_blocks:

    print(block)
    print()