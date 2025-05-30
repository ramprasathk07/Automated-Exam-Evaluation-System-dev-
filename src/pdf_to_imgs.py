import fitz
from PIL import Image
import os


def pdf_to_images(pdf_path):
    """Converts each page of a PDF file to a PNG image."""
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = os.path.join("Evaluation_bot", pdf_name)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # print("INSIDe", pdf_path) # Optional: replace with logging
    pdf_document = None  # Initialize to None
    try:
        pdf_document = fitz.open(pdf_path)
        # total_pages = pdf_document.page_count # Not strictly needed

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image_output_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
            image.save(image_output_path)
            # print(f"Saved {image_output_path}") # Optional: replace with logging
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        # Optionally re-raise or handle more gracefully if output_folder might not be valid
        raise
    finally:
        if pdf_document:
            pdf_document.close()
            # print(f"All pages saved in: {output_folder}") # Optional: replace with logging
    return output_folder
