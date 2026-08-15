import fitz  # PyMuPDF


def detect_pdf_type(pdf_path):
    """
    Detect whether a PDF is text-based or image-based.

    The function checks ALL pages in the PDF.

    Returns:
        "text"  -> PDF contains meaningful extractable text
        "image" -> PDF contains little/no extractable text
    """

    document = fitz.open(pdf_path)

    total_pages = len(document)
    total_text_characters = 0
    pages_with_text = 0

    for page in document:
        page_text = page.get_text().strip()

        if page_text:
            pages_with_text += 1
            total_text_characters += len(page_text)

    document.close()

    # If meaningful text is found across the document,
    # treat it as a text-based PDF.
    if total_text_characters > 50:
        pdf_type = "text"
    else:
        pdf_type = "image"

    return pdf_type