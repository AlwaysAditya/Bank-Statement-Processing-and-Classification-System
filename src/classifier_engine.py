import pandas as pd

from src.classifier import classify_transactions
from src.ml_classifier import (
    ml_classify_transactions,
    is_ml_model_available,
)


def hybrid_classify_transactions(
    transactions_df
):
    """
    Hybrid transaction classification engine.

    Classification priority:

        1. Existing heuristic/rule-based classifier
        2. Traditional ML classifier
        3. Uncategorized fallback

    The system does NOT use an LLM.
    """

    if transactions_df is None:
        raise ValueError(
            "transactions_df cannot be None."
        )

    if not isinstance(
        transactions_df,
        pd.DataFrame
    ):
        raise TypeError(
            "transactions_df must be a pandas DataFrame."
        )

    if transactions_df.empty:
        return transactions_df

    df = transactions_df.copy()

    # ========================================================
    # 1. HEURISTIC CLASSIFICATION
    # ========================================================

    try:

        rule_based_df = classify_transactions(
            df.copy()
        )

    except Exception as e:

        print(
            f"Rule-based classification failed: {e}"
        )

        rule_based_df = df.copy()

    # ========================================================
    # FIND CATEGORY COLUMN
    # ========================================================

    category_column = None

    for column in rule_based_df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
        )

        if normalized in [
            "category",
            "classification",
            "transaction_category",
        ]:

            category_column = column
            break

    # ========================================================
    # IF RULE-BASED CLASSIFIER DID NOT CREATE CATEGORY
    # ========================================================

    if category_column is None:

        rule_based_df["Category"] = (
            "Uncategorized"
        )

        category_column = "Category"

    # ========================================================
    # 2. TRADITIONAL ML CLASSIFICATION
    # ========================================================

    if is_ml_model_available():

        try:

            ml_df = ml_classify_transactions(
                rule_based_df.copy()
            )

            if (
                isinstance(
                    ml_df,
                    pd.DataFrame
                )
                and
                not ml_df.empty
            ):

                # ------------------------------------------------
                # Prefer ML result only where rule classifier
                # produced Uncategorized.
                # ------------------------------------------------

                ml_category_column = None

                for column in ml_df.columns:

                    normalized = (
                        str(column)
                        .strip()
                        .lower()
                    )

                    if normalized in [
                        "ml_category",
                        "predicted_category",
                        "ml_classification",
                    ]:

                        ml_category_column = column
                        break

                if ml_category_column is not None:

                    mask = (
                        rule_based_df[
                            category_column
                        ]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .isin([
                            "",
                            "uncategorized",
                            "unknown",
                            "other",
                        ])
                    )

                    rule_based_df.loc[
                        mask,
                        category_column
                    ] = (
                        ml_df.loc[
                            mask,
                            ml_category_column
                        ]
                        .values
                    )

        except Exception as e:

            print(
                f"ML classification skipped: {e}"
            )

    # ========================================================
    # 3. FINAL FALLBACK
    # ========================================================

    rule_based_df[
        category_column
    ] = (
        rule_based_df[
            category_column
        ]
        .fillna("Uncategorized")
        .replace(
            "",
            "Uncategorized"
        )
    )

    # ========================================================
    # 4. CLASSIFICATION METHOD
    # ========================================================

    rule_based_df[
        "Classification Method"
    ] = "Heuristic / Rule-Based"

    return rule_based_df