import re
import pandas as pd


DATE_PATTERN = re.compile(
    r"^\d{2}/\d{2}/\d{4}$"
)

AMOUNT_PATTERN = re.compile(
    r"^[\d,]+\.\d{2}$"
)


def clean_amount(value):
    """Convert an amount string into float."""

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = (
        value.replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("£", "")
        .replace("€", "")
    )

    try:
        return float(value)

    except ValueError:
        return None


def is_date(value):
    """Check whether a value is DD/MM/YYYY."""

    return bool(
        DATE_PATTERN.match(
            str(value).strip()
        )
    )


def is_amount(value):
    """Check whether a value is a monetary amount."""

    return bool(
        AMOUNT_PATTERN.match(
            str(value).strip()
        )
    )


def extract_transactions(text):
    """
    Extract transactions from PDF text.

    Expected table:

    Date
    Merchant / Description
    Debit
    Credit
    Balance

    Category is intentionally NOT extracted.
    Classification happens later.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    transactions = []

    i = 0

    while i < len(lines):

        # ----------------------------------------------------
        # Look for transaction date
        # ----------------------------------------------------

        if not is_date(lines[i]):
            i += 1
            continue

        date = lines[i]

        # ----------------------------------------------------
        # Need at least description + amount + balance
        # ----------------------------------------------------

        if i + 3 >= len(lines):
            break

        description = lines[i + 1]

        # ----------------------------------------------------
        # Ignore table headers accidentally encountered
        # ----------------------------------------------------

        if description.lower() in {
            "merchant / description",
            "description",
            "date",
            "debit",
            "credit",
            "balance",
        }:
            i += 1
            continue

        # ----------------------------------------------------
        # Find monetary values belonging to this transaction
        #
        # Typical PDF extraction:
        #
        # DATE
        # DESCRIPTION
        # DEBIT/CREDIT
        # BALANCE
        #
        # Therefore we collect the next two amounts.
        # ----------------------------------------------------

        amounts = []

        j = i + 2

        while (
            j < len(lines)
            and len(amounts) < 2
        ):

            current = lines[j]

            # Stop if another transaction starts
            if is_date(current):
                break

            if is_amount(current):
                amounts.append(current)

            j += 1

        # We need amount + balance
        if len(amounts) < 2:
            i += 1
            continue

        transaction_amount = amounts[0]
        balance = amounts[1]

        # ----------------------------------------------------
        # Determine Debit / Credit
        # ----------------------------------------------------

        description_upper = description.upper()

        debit = None
        credit = None

        # Income / credit transactions
        credit_keywords = [
            "SALARY",
            "CREDIT",
            "REFUND",
            "CASHBACK",
            "CLIENT PAYMENT",
            "FREELANCE PAYMENT",
            "TRANSFER CREDIT",
        ]

        is_credit = any(
            keyword in description_upper
            for keyword in credit_keywords
        )

        if is_credit:
            credit = clean_amount(
                transaction_amount
            )
        else:
            debit = clean_amount(
                transaction_amount
            )

        transactions.append({
            "Date": date,
            "Description": description,
            "Debit": debit,
            "Credit": credit,
            "Balance": clean_amount(balance),
        })

        # Move to the next likely transaction
        i = j

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    columns = [
        "Date",
        "Description",
        "Debit",
        "Credit",
        "Balance",
    ]

    df = pd.DataFrame(
        transactions,
        columns=columns,
    )

    if df.empty:
        return df

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d/%m/%Y",
        errors="coerce",
    )

    return df


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def extract_transaction_rows(text):
    """
    Compatibility wrapper.
    """

    df = extract_transactions(text)

    return df.to_dict(
        orient="records"
    )