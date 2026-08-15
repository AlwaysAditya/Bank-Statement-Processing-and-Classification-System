from pathlib import Path

from src.pdf_detector import detect_pdf_type
from src.text_processor import process_text_pdf
from src.ocr_processor import process_image_pdf
from src.transaction_extractor import extract_transactions
from src.validator import validate_transactions
from src.classifier import classify_transactions


def process_statement(pdf_path):
    """
    Complete bank statement processing pipeline.

    Flow:

        PDF
        ↓
        Detect PDF type
        ↓
        Text PDF → text_processor
        Image PDF → ocr_processor
        ↓
        Transaction extraction
        ↓
        Validation
        ↓
        Classification
        ↓
        Final DataFrame
    """

    pdf_path = Path(pdf_path)

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

        extracted_content = process_text_pdf(
            str(pdf_path)
        )

    elif pdf_type == "image":

        print(
            "\nUsing OCR processor..."
        )

        extracted_content = process_image_pdf(
            str(pdf_path)
        )

    else:

        raise ValueError(
            f"Unsupported PDF type: {pdf_type}"
        )

    # ========================================================
    # 4. EXTRACT TRANSACTIONS
    # ========================================================

    print(
        "\nExtracting transactions..."
    )

    transactions_df = extract_transactions(
        extracted_content
    )

    # ========================================================
    # 5. VALIDATE
    # ========================================================

    print(
        "\nValidating transactions..."
    )

    transactions_df, validation_results = (
        validate_transactions(
            transactions_df
        )
    )

    if not validation_results["valid"]:

        raise ValueError(
            "Transaction validation failed: "
            + validation_results["message"]
        )

    # ========================================================
    # 6. CLASSIFY
    # ========================================================

    print(
        "\nClassifying transactions..."
    )

    transactions_df = classify_transactions(
        transactions_df
    )

    # ========================================================
    # 7. FINAL RESULT
    # ========================================================

    print(
        "\nProcessing completed successfully."
    )

    print(
        f"Transactions processed: "
        f"{len(transactions_df)}"
    )

    print("=" * 70)

    return transactions_df