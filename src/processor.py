from pathlib import Path

from src.pdf_detector import detect_pdf_type
from src.text_processor import process_text_pdf
from src.ocr_processor import process_image_pdf
from src.transaction_extractor import extract_transactions
from src.validator import validate_transactions
from src.classifier_engine import hybrid_classify_transactions


def process_statement(pdf_path):
    """
    Complete bank statement processing pipeline.

    Returns
    -------
    tuple
        (
            account_details,
            transactions_df
        )

    Flow:

        PDF
          ↓
        Detect PDF Type
          ↓
        Text PDF / OCR
          ↓
        Extract Account Details
          ↓
        Extract Transactions
          ↓
        Validate
          ↓
        Hybrid Classification
          ↓
        Return account details + transactions
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

    print(f"\nInput PDF: {pdf_path}")

    # ========================================================
    # 2. DETECT PDF TYPE
    # ========================================================

    pdf_type = detect_pdf_type(
        str(pdf_path)
    )

    print(f"PDF Type: {pdf_type}")

    # ========================================================
    # 3. EXTRACT CONTENT
    # ========================================================

    if pdf_type == "text":

        print("\nUsing text PDF processor...")

        extracted_content = process_text_pdf(
            str(pdf_path)
        )

    elif pdf_type == "image":

        print("\nUsing OCR processor...")

        extracted_content = process_image_pdf(
            str(pdf_path)
        )

    else:

        raise ValueError(
            f"Unsupported PDF type: {pdf_type}"
        )

    # ========================================================
    # 4. EXTRACT ACCOUNT DETAILS
    # ========================================================

    print("\nExtracting account details...")

    account_details = extract_account_details(
        extracted_content
    )

    print(
        f"Account Holder: "
        f"{account_details.get('account_holder', 'Not found')}"
    )

    print(
        f"Account Number: "
        f"{account_details.get('account_number', 'Not found')}"
    )

    print(
        f"IFSC: "
        f"{account_details.get('ifsc', 'Not found')}"
    )

    # ========================================================
    # 5. EXTRACT TRANSACTIONS
    # ========================================================

    print("\nExtracting transactions...")

    transactions_df = extract_transactions(
        extracted_content
    )

    # ========================================================
    # 6. VALIDATE
    # ========================================================

    print("\nValidating transactions...")

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
    # 7. CLASSIFICATION
    # ========================================================

    print("\nClassifying transactions...")

    transactions_df = hybrid_classify_transactions(
        transactions_df
    )

    # ========================================================
    # 8. FINAL RESULT
    # ========================================================

    print(
        "\nProcessing completed successfully."
    )

    print(
        f"Transactions processed: "
        f"{len(transactions_df)}"
    )

    print("=" * 70)

    return account_details, transactions_df


# ============================================================
# ACCOUNT DETAILS EXTRACTION
# ============================================================

def extract_account_details(extracted_content):
    """
    Extract account-level information from extracted PDF/OCR
    content using regular expressions and heuristics.

    No LLM is used.
    """

    import re

    # --------------------------------------------------------
    # Normalize content
    # --------------------------------------------------------

    if isinstance(extracted_content, str):

        text = extracted_content

    elif isinstance(extracted_content, list):

        text = "\n".join(
            str(item)
            for item in extracted_content
        )

    elif isinstance(extracted_content, dict):

        text_parts = []

        for value in extracted_content.values():

            if isinstance(value, str):
                text_parts.append(value)

            elif isinstance(value, list):

                text_parts.extend(
                    str(x)
                    for x in value
                )

        text = "\n".join(text_parts)

    else:

        text = str(extracted_content)

    # Normalize whitespace
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    details = {
        "bank_name": None,
        "account_holder": None,
        "account_number": None,
        "ifsc": None,
        "branch": None,
        "statement_period": None,
    }

    # ========================================================
    # BANK NAME
    # ========================================================

    bank_patterns = [
        r"(?:Bank\s*Name|Bank)\s*[:\-]\s*(.+)",
    ]

    for pattern in bank_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            details["bank_name"] = (
                match.group(1)
                .strip()
                .split("\n")[0]
            )

            break

    # Common Indian banks fallback
    if not details["bank_name"]:

        banks = [
            "HDFC Bank",
            "ICICI Bank",
            "State Bank of India",
            "Axis Bank",
            "Kotak Mahindra Bank",
            "IndusInd Bank",
            "Yes Bank",
            "IDFC FIRST Bank",
            "Federal Bank",
            "Bank of Baroda",
            "Punjab National Bank",
            "Canara Bank",
            "Union Bank of India",
            "Bank of India",
            "Indian Bank",
            "IDBI Bank",
            "RBL Bank",
            "Bandhan Bank",
        ]

        for bank in banks:

            if bank.lower() in text.lower():

                details["bank_name"] = bank
                break

    # ========================================================
    # ACCOUNT HOLDER
    # ========================================================

    holder_patterns = [
        r"(?:Account\s*Holder|Customer|Name)\s*[:\-]\s*([A-Za-z][A-Za-z .]+)",
    ]

    for pattern in holder_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            details["account_holder"] = (
                match.group(1)
                .strip()
            )

            break

    # ========================================================
    # ACCOUNT NUMBER
    # ========================================================

    account_patterns = [
        r"(?:Account\s*(?:Number|No\.?|#)|A\/C\s*(?:Number|No\.?))"
        r"\s*[:\-]?\s*([A-Za-z0-9\-]{6,30})",
    ]

    for pattern in account_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            details["account_number"] = (
                match.group(1)
                .strip()
            )

            break

    # ========================================================
    # IFSC
    # ========================================================

    ifsc_match = re.search(
        r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        text,
        re.IGNORECASE
    )

    if ifsc_match:

        details["ifsc"] = (
            ifsc_match.group(0)
            .upper()
        )

    else:

        ifsc_label_match = re.search(
            r"IFSC\s*(?:Code)?\s*[:\-]?\s*([A-Z0-9]{11})",
            text,
            re.IGNORECASE
        )

        if ifsc_label_match:

            details["ifsc"] = (
                ifsc_label_match.group(1)
                .upper()
            )

    # ========================================================
    # BRANCH
    # ========================================================

    branch_match = re.search(
        r"(?:Branch|Branch\s*Name|Branch\s*/\s*City)"
        r"\s*[:\-]\s*(.+)",
        text,
        re.IGNORECASE
    )

    if branch_match:

        details["branch"] = (
            branch_match.group(1)
            .strip()
            .split("\n")[0]
        )

    # ========================================================
    # STATEMENT PERIOD
    # ========================================================

    period_match = re.search(
        r"(?:Statement\s*Period|Period)"
        r"\s*[:\-]\s*"
        r"(.+?)"
        r"(?:\n|$)",
        text,
        re.IGNORECASE
    )

    if period_match:

        details["statement_period"] = (
            period_match.group(1)
            .strip()
        )

    return details