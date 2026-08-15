import re


# ============================================================
# ACCOUNT INFORMATION EXTRACTION
# ============================================================

def _clean_value(value):
    """
    Clean extracted account information.
    """

    if value is None:
        return None

    value = str(value).strip()

    # Remove excessive whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip(" :-|")


# ============================================================
# ACCOUNT NUMBER
# ============================================================

def extract_account_number(text):
    """
    Extract account number from bank statement text.

    Supports common variations such as:

        Account Number
        Account No
        A/C No
        A/C Number
        A/C #
        Account #
    """

    patterns = [

        r"(?:account\s*(?:number|no\.?|#))"
        r"\s*[:\-]?\s*([A-Z0-9X*]{6,30})",

        r"(?:a/c\s*(?:number|no\.?|#))"
        r"\s*[:\-]?\s*([A-Z0-9X*]{6,30})",

        r"(?:a\/c\s*(?:number|no\.?|#))"
        r"\s*[:\-]?\s*([A-Z0-9X*]{6,30})",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return _clean_value(
                match.group(1)
            )

    return None


# ============================================================
# IFSC
# ============================================================

def extract_ifsc(text):
    """
    Extract Indian IFSC code.

    Example:

        HDFC0001234
        SBIN0001234
        ICIC0001234
    """

    # Standard IFSC format:
    # 4 alphabetic characters
    # 0
    # 6 alphanumeric characters

    pattern = (
        r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(0).upper()

    # Try labelled IFSC field as fallback

    labelled_pattern = (
        r"(?:IFSC\s*(?:CODE)?|IFSC)"
        r"\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})"
    )

    match = re.search(
        labelled_pattern,
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).upper()

    return None


# ============================================================
# ACCOUNT HOLDER NAME
# ============================================================

def extract_account_holder_name(text):
    """
    Extract account holder name.

    Supports common labels such as:

        Account Holder
        Account Holder Name
        Customer Name
        Name
        A/C Holder
    """

    patterns = [

        r"(?:account\s*holder\s*name)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z .'-]{2,100})",

        r"(?:account\s*holder)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z .'-]{2,100})",

        r"(?:customer\s*name)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z .'-]{2,100})",

        r"(?:a/c\s*holder)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z .'-]{2,100})",

        r"(?:name)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z .'-]{2,100})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = _clean_value(
                match.group(1)
            )

            # Avoid accidentally capturing common field names
            invalid_values = {
                "account number",
                "account no",
                "account no.",
                "ifsc",
                "ifsc code",
                "branch",
                "address",
                "statement period",
                "date",
            }

            if value.lower() not in invalid_values:

                return value

    return None


# ============================================================
# BANK NAME
# ============================================================

def extract_bank_name(text):
    """
    Extract bank name from labelled fields.

    Supports:

        Bank Name: HDFC Bank
        Bank: State Bank of India
    """

    patterns = [

        r"(?:bank\s*name)"
        r"\s*[:\-]?\s*([A-Za-z0-9&.' -]{3,100})",

        r"(?:bank)"
        r"\s*[:\-]\s*([A-Za-z0-9&.' -]{3,100})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return _clean_value(
                match.group(1)
            )

    # Common Indian bank names as fallback

    banks = [

        "State Bank of India",
        "SBI",
        "HDFC Bank",
        "ICICI Bank",
        "Axis Bank",
        "Kotak Mahindra Bank",
        "Bank of Baroda",
        "Punjab National Bank",
        "Canara Bank",
        "Union Bank of India",
        "IndusInd Bank",
        "IDFC FIRST Bank",
        "Yes Bank",
        "Federal Bank",
        "Bank of India",
        "Indian Bank",
        "Central Bank of India",
    ]

    text_lower = text.lower()

    for bank in banks:

        if bank.lower() in text_lower:

            return bank

    return None


# ============================================================
# BRANCH
# ============================================================

def extract_branch(text):
    """
    Extract bank branch information.
    """

    patterns = [

        r"(?:branch\s*name)"
        r"\s*[:\-]?\s*([A-Za-z0-9&.'()\/ -]{2,100})",

        r"(?:branch)"
        r"\s*[:\-]\s*([A-Za-z0-9&.'()\/ -]{2,100})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return _clean_value(
                match.group(1)
            )

    return None


# ============================================================
# STATEMENT PERIOD
# ============================================================

def extract_statement_period(text):
    """
    Extract statement period.

    Examples:

        Statement Period: 01/04/2026 - 30/04/2026

        Period:
        01-04-2026 to 30-04-2026
    """

    patterns = [

        r"(?:statement\s*period|period)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
        r"\s*(?:to|\-|–|—)"
        r"\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            start_date = match.group(1)
            end_date = match.group(2)

            return f"{start_date} - {end_date}"

    return None


# ============================================================
# MAIN EXTRACTION FUNCTION
# ============================================================

def extract_account_details(text):
    """
    Extract all available account information
    from bank statement text.

    Returns:
        dict
    """

    if text is None:

        text = ""

    text = str(text)

    account_details = {

        "bank_name": extract_bank_name(
            text
        ),

        "account_holder_name": (
            extract_account_holder_name(
                text
            )
        ),

        "account_number": (
            extract_account_number(
                text
            )
        ),

        "ifsc": extract_ifsc(
            text
        ),

        "branch": extract_branch(
            text
        ),

        "statement_period": (
            extract_statement_period(
                text
            )
        ),
    }

    return account_details