from pathlib import Path

from src.pdf_detector import detect_pdf_type
from src.text_processor import process_text_pdf
from src.ocr_processor import process_image_pdf
from src.transaction_extractor import extract_transactions
from src.validator import validate_transactions
from src.classifier_engine import hybrid_classify_transactions
from src.account_extractor import extract_account_details


def _get_text_for_account_extraction(extracted_content):
    """
    Convert extracted PDF/OCR output into plain text
    suitable for account information extraction.
    """

    if extracted_content is None:

        return ""


    # --------------------------------------------------------
    # Plain string
    # --------------------------------------------------------

    if isinstance(
        extracted_content,
        str
    ):

        return extracted_content


    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(
        extracted_content,
        dict
    ):

        possible_keys = [
            "text",
            "content",
            "raw_text",
            "extracted_text"
        ]

        for key in possible_keys:

            if key in extracted_content:

                value = extracted_content[key]

                if value is not None:

                    return str(value)


        # Last resort
        return str(
            extracted_content
        )


    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    if isinstance(
        extracted_content,
        list
    ):

        return "\n".join(
            str(item)
            for item in extracted_content
        )


    return str(
        extracted_content
    )


# ============================================================
# MAIN PROCESSING PIPELINE
# ============================================================

def process_statement(pdf_path):

    """
    Complete bank statement processing pipeline.

    Flow:

        PDF
        ↓
        Detect PDF type
        ↓
        Text PDF / Image PDF
        ↓
        Account Information Extraction
        ↓
        Transaction Extraction
        ↓
        Validation
        ↓
        Hybrid Classification
        ↓
        Final Data
    """

    pdf_path = Path(
        pdf_path
    )


    # ========================================================
    # 1. CHECK FILE
    # ========================================================

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )


    if pdf_path.suffix.lower() != ".pdf":

        raise ValueError(
            "Input file must be a PDF."
        )


    print("=" * 70)
    print("BANK STATEMENT PROCESSING")
    print("=" * 70)


    print(
        f"\nInput PDF: {pdf_path}"
    )


    # ========================================================
    # 2. DETECT PDF TYPE
    # ========================================================

    pdf_type = detect_pdf_type(
        str(pdf_path)
    )


    print(
        f"PDF Type: {pdf_type}"
    )


    # ========================================================
    # 3. EXTRACT TEXT
    # ========================================================

    if pdf_type == "text":

        print(
            "\nUsing text PDF processor..."
        )

        extracted_content = (
            process_text_pdf(
                str(pdf_path)
            )
        )


    elif pdf_type == "image":

        print(
            "\nUsing OCR processor..."
        )

        extracted_content = (
            process_image_pdf(
                str(pdf_path)
            )
        )


    else:

        raise ValueError(
            f"Unsupported PDF type: {pdf_type}"
        )


    # ========================================================
    # 4. CONVERT TO TEXT
    # ========================================================

    extracted_text = (
        _get_text_for_account_extraction(
            extracted_content
        )
    )


    # ========================================================
    # 5. EXTRACT ACCOUNT DETAILS
    # ========================================================

    print(
        "\nExtracting account information..."
    )


    account_details = (
        extract_account_details(
            extracted_text
        )
    )


    print(
        "\nAccount Details:"
    )


    for key, value in (
        account_details.items()
    ):

        print(
            f"  {key}: {value}"
        )


    # ========================================================
    # 6. EXTRACT TRANSACTIONS
    # ========================================================

    print(
        "\nExtracting transactions..."
    )


    transactions_df = (
        extract_transactions(
            extracted_content
        )
    )


    # ========================================================
    # 7. VALIDATE
    # ========================================================

    print(
        "\nValidating transactions..."
    )


    (
        transactions_df,
        validation_results
    ) = validate_transactions(
        transactions_df
    )


    if not validation_results["valid"]:

        raise ValueError(
            "Transaction validation failed: "
            + validation_results["message"]
        )


    # ========================================================
    # 8. CLASSIFICATION
    # ========================================================

    print(
        "\nClassifying transactions..."
    )


    transactions_df = (
        hybrid_classify_transactions(
            transactions_df
        )
    )


    # ========================================================
    # 9. FINAL RESULT
    # ========================================================

    print(
        "\nProcessing completed successfully."
    )


    print(
        f"Transactions processed: "
        f"{len(transactions_df)}"
    )


    print("=" * 70)


    # ========================================================
    # RETURN BOTH
    # ========================================================

    return (
        transactions_df,
        account_details
    )