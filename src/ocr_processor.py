import fitz  # PyMuPDF
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io


def process_image_pdf(pdf_path):
    """
    Extract text from every page of an image-based PDF
    using Tesseract OCR.

    Returns:
        str: Combined OCR text from all pages.
    """

    document = fitz.open(pdf_path)

    pages = []

    try:

        for page_number, page in enumerate(document):

            # Render PDF page as image
            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )

            image_bytes = pix.tobytes(
                "png"
            )

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            # OCR
            text = pytesseract.image_to_string(
                image
            )

            if text:
                pages.append(text)

    finally:

        document.close()

    return "\n".join(pages)

def preprocess_image(page):
    """
    Convert a PDF page into a clean image suitable for OCR.
    """

    # Render PDF page at 300 DPI
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(300 / 72, 300 / 72),
        alpha=False
    )

    # Convert PyMuPDF image to NumPy array
    image = np.frombuffer(
        pixmap.samples,
        dtype=np.uint8
    )

    image = image.reshape(
        pixmap.height,
        pixmap.width,
        pixmap.n
    )

    # Convert RGB image to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2GRAY
    )

    # Remove noise
    denoised = cv2.fastNlMeansDenoising(
        gray,
        None,
        10,
        7,
        21
    )

    # Improve contrast
    threshold = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return threshold


def extract_text_from_image_pdf(pdf_path):
    """
    Extract OCR text from every page of an image/scanned PDF.

    Returns:
        {
            "page_count": int,
            "pages": [
                {
                    "page_number": int,
                    "text": str
                }
            ],
            "full_text": str
        }
    """

    pages = []

    try:

        document = fitz.open(pdf_path)

        page_count = len(document)

        for page_number, page in enumerate(
            document,
            start=1
        ):

            processed_image = preprocess_image(page)

            text = pytesseract.image_to_string(
                processed_image,
                config="--psm 6"
            ).strip()

            pages.append({
                "page_number": page_number,
                "text": text
            })

        document.close()

        full_text = "\n".join(
            page["text"]
            for page in pages
        )

        return {
            "page_count": page_count,
            "pages": pages,
            "full_text": full_text
        }

    except Exception as e:

        raise RuntimeError(
            f"OCR processing failed: {e}"
        )