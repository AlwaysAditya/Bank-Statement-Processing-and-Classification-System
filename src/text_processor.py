import fitz  # PyMuPDF
import pdfplumber

def process_text_pdf(pdf_path):
    """
    Extract text from every page of a text-based PDF.

    Returns:
        str: Combined text from all pages.
    """

    document = fitz.open(pdf_path)

    pages = []

    try:
        for page_number, page in enumerate(document):

            text = page.get_text("text")

            if text:
                pages.append(text)

    finally:
        document.close()

    return "\n".join(pages)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from every page of a text-based PDF.

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
        # ----------------------------------------------------
        # First extraction method: PyMuPDF
        # ----------------------------------------------------
        document = fitz.open(pdf_path)

        page_count = len(document)

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text").strip()

            pages.append({
                "page_number": page_number,
                "text": text
            })

        document.close()

        # Combine all pages
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
            f"Failed to extract text from PDF: {e}"
        )


def extract_tables_from_pdf(pdf_path):
    """
    Extract tables from every page using pdfplumber.

    Returns:
        {
            "page_count": int,
            "tables": [
                {
                    "page_number": int,
                    "tables": [...]
                }
            ]
        }
    """

    pages_with_tables = []

    try:

        with pdfplumber.open(pdf_path) as pdf:

            page_count = len(pdf.pages)

            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                tables = page.extract_tables()

                pages_with_tables.append({
                    "page_number": page_number,
                    "tables": tables
                })

        return {
            "page_count": page_count,
            "pages": pages_with_tables
        }

    except Exception as e:

        raise RuntimeError(
            f"Failed to extract tables from PDF: {e}"
        )