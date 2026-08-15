import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Description",
    "Debit",
    "Credit",
    "Balance",
]


def validate_columns(df):
    """
    Check whether all required transaction columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return False, (
            f"Missing columns: {missing_columns}"
        )

    return True, "All required columns present."


def validate_empty_rows(df):
    """
    Remove completely empty transaction rows.
    """

    if df.empty:
        return df

    df = df.dropna(
        how="all"
    ).reset_index(
        drop=True
    )

    return df


def validate_dates(df):
    """
    Check that transaction dates are valid.
    """

    invalid_dates = df[
        df["Date"].isna()
    ]

    if not invalid_dates.empty:

        return False, (
            f"{len(invalid_dates)} invalid date(s) found."
        )

    return True, "All dates are valid."


def validate_amounts(df):
    """
    Validate debit, credit and balance values.
    """

    for column in [
        "Debit",
        "Credit",
        "Balance",
    ]:

        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):

            return False, (
                f"{column} contains non-numeric values."
            )

    return True, "All monetary values are valid."


def validate_debit_credit(df):
    """
    A transaction should normally have either
    debit OR credit, not both.
    """

    invalid_rows = df[
        (
            df["Debit"].notna()
            & df["Credit"].notna()
        )
    ]

    if not invalid_rows.empty:

        return False, (
            f"{len(invalid_rows)} row(s) "
            "contain both debit and credit."
        )

    return True, "Debit/Credit structure is valid."


def validate_transactions(df):
    """
    Run all transaction validation checks.

    Returns:

        cleaned_dataframe
        validation_results
    """

    results = {}

    # --------------------------------------------------------
    # Remove empty rows
    # --------------------------------------------------------

    df = validate_empty_rows(df)

    if df.empty:

        return df, {
            "valid": False,
            "message": "No transactions found."
        }

    # --------------------------------------------------------
    # Column validation
    # --------------------------------------------------------

    columns_valid, message = validate_columns(
        df
    )

    results["columns"] = message

    if not columns_valid:

        return df, {
            "valid": False,
            "message": message,
        }

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    dates_valid, message = validate_dates(
        df
    )

    results["dates"] = message

    # --------------------------------------------------------
    # Amount validation
    # --------------------------------------------------------

    amounts_valid, message = validate_amounts(
        df
    )

    results["amounts"] = message

    # --------------------------------------------------------
    # Debit/Credit validation
    # --------------------------------------------------------

    debit_credit_valid, message = (
        validate_debit_credit(df)
    )

    results["debit_credit"] = message

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    results["valid"] = (
        columns_valid
        and dates_valid
        and amounts_valid
        and debit_credit_valid
    )

    if results["valid"]:

        results["message"] = (
            "Transaction validation successful."
        )

    else:

        results["message"] = (
            "Transaction validation failed."
        )

    return df, results