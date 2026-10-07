import pymupdf
import os


def extract_images_from_pdf(file_path, output_dir="extracted_images"):
    """
    Extract embedded images from a PDF.

    Returns a list containing:
    - page number
    - image number
    - saved image path
    """

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    document = pymupdf.open(file_path)

    extracted_images = []

    for page_number, page in enumerate(
        document,
        start=1
    ):

        images = page.get_images(
            full=True
        )

        for image_number, image in enumerate(
            images,
            start=1
        ):

            xref = image[0]

            try:

                image_data = document.extract_image(
                    xref
                )

                extension = image_data[
                    "ext"
                ]

                image_bytes = image_data[
                    "image"
                ]

                filename = (
                    f"page_{page_number}_"
                    f"image_{image_number}."
                    f"{extension}"
                )

                output_path = os.path.join(
                    output_dir,
                    filename
                )

                with open(
                    output_path,
                    "wb"
                ) as image_file:

                    image_file.write(
                        image_bytes
                    )

                extracted_images.append({
                    "page": page_number,
                    "image": image_number,
                    "path": output_path,
                    "extension": extension
                })

            except Exception as e:

                print(
                    f"Warning: Could not extract "
                    f"image on page "
                    f"{page_number}: {e}"
                )

    document.close()

    return extracted_images