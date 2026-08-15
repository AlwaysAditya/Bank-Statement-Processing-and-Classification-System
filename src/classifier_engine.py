import pandas as pd

from src.classifier import classify_transactions as rule_classifier
from src.ml_classifier import predict_transaction


# ============================================================
# FIND DESCRIPTION COLUMN
# ============================================================

def find_description_column(df):

    possible_columns = [
        "Description",
        "description",
        "Transaction Description",
        "transaction_description",
        "Narration",
        "narration",
        "Details",
        "details",
        "Particulars",
        "particulars",
    ]

    for column in possible_columns:

        if column in df.columns:
            return column

    raise ValueError(
        "Could not find transaction description column. "
        f"Available columns: {list(df.columns)}"
    )


# ============================================================
# CHECK WHETHER RULE CLASSIFIER FOUND A CATEGORY
# ============================================================

def is_valid_rule_category(category):

    if pd.isna(category):
        return False

    category = str(category).strip().lower()

    invalid_categories = {
        "",
        "other",
        "unknown",
        "unclassified",
        "none",
        "nan",
    }

    return category not in invalid_categories


# ============================================================
# HYBRID CLASSIFICATION
# ============================================================

def hybrid_classify_transactions(
    df,
    confidence_threshold=0.50
):

    if df is None:

        raise ValueError(
            "Input DataFrame cannot be None."
        )

    if df.empty:

        return df.copy()


    result = df.copy()


    # ========================================================
    # 1. FIND DESCRIPTION COLUMN
    # ========================================================

    description_column = (
        find_description_column(result)
    )


    # ========================================================
    # 2. RUN EXISTING RULE CLASSIFIER
    # ========================================================

    rule_result = rule_classifier(
        result.copy()
    )


    # ========================================================
    # 3. FIND CATEGORY COLUMN
    # ========================================================

    category_column = None

    for column in [
        "Category",
        "category",
        "Transaction Category",
        "transaction_category",
    ]:

        if column in rule_result.columns:

            category_column = column
            break


    if category_column is None:

        raise ValueError(
            "Rule classifier did not create a category column."
        )


    # ========================================================
    # 4. CLASSIFY EACH TRANSACTION
    # ========================================================

    final_categories = []

    classification_methods = []

    classification_confidences = []


    for index, description in enumerate(
        result[description_column]
    ):

        rule_category = (
            rule_result.iloc[index][
                category_column
            ]
        )


        # ====================================================
        # RULE-BASED CLASSIFICATION
        # ====================================================

        if is_valid_rule_category(
            rule_category
        ):

            final_categories.append(
                rule_category
            )

            classification_methods.append(
                "Rule-Based"
            )

            classification_confidences.append(
                1.0
            )

            continue


        # ====================================================
        # ML CLASSIFICATION
        # ====================================================

        ml_category, ml_confidence = (
            predict_transaction(
                description,
                confidence_threshold
            )
        )


        if ml_category != "Other":

            final_categories.append(
                ml_category
            )

            classification_methods.append(
                "TF-IDF + Logistic Regression"
            )

            classification_confidences.append(
                ml_confidence
            )

        else:

            final_categories.append(
                "Other"
            )

            classification_methods.append(
                "Unclassified"
            )

            classification_confidences.append(
                ml_confidence
            )


    # ========================================================
    # 5. ADD RESULTS
    # ========================================================

    result["Category"] = final_categories

    result["Classification Method"] = (
        classification_methods
    )

    result["Classification Confidence"] = [
        round(
            confidence * 100,
            2
        )
        for confidence in classification_confidences
    ]


    return result