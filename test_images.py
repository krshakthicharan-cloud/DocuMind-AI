from document_processing.image_extractor import (
    extract_images_from_pdf
)


PDF_PATH = r"C:\Users\SHAKTHI  CHARAN KR\Downloads\DSA_Unit1_Theory (1).pdf"
print("Extracting images...")

images = extract_images_from_pdf(
    PDF_PATH
)

print(
    f"\nFound {len(images)} images."
)

for image in images:

    print(
        f"Page: {image['page']} | "
        f"Image: {image['image']} | "
        f"File: {image['path']}"
    )