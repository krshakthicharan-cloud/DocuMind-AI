import pymupdf


def extract_tables_from_pdf(file_path):
    """
    Detect tables and extract the text contained in each
    table region.

    The PDF's normal text layer is used because it preserves
    the actual table content better than table.extract()
    for this document.
    """

    document = pymupdf.open(file_path)

    tables = []

    for page_number, page in enumerate(
        document,
        start=1
    ):

        try:

            finder = page.find_tables()

            if not finder:
                continue

            for table_number, table in enumerate(
                finder.tables,
                start=1
            ):

                bbox = table.bbox

                text = page.get_text(
                    "text",
                    clip=bbox
                ).strip()

                if not text:
                    continue

                tables.append({
                    "page": page_number,
                    "table": table_number,
                    "text": text
                })

        except Exception as e:

            print(
                f"Warning: Could not process table "
                f"on page {page_number}: {e}"
            )

    document.close()

    return tables


def tables_to_text(tables):

    text_blocks = []

    for table in tables:

        block = (
            f"Table {table['table']} "
            f"(Page {table['page']})\n"
            f"{table['text']}"
        )

        text_blocks.append(block)

    return text_blocks