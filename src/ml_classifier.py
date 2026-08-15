from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "transaction_classifier.pkl"
)


def is_ml_model_available():
    """
    Check whether the trained ML model exists.
    """

    return MODEL_PATH.exists()


def ml_classify_transactions(
    transactions_df
):
    """
    Classify transactions using the trained
    traditional ML model.
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

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found: {MODEL_PATH}"
        )

    model_data = joblib.load(
        MODEL_PATH
    )

    # --------------------------------------------------------
    # Support either a saved pipeline or dictionary
    # --------------------------------------------------------

    if isinstance(
        model_data,
        dict
    ):

        model = model_data.get(
            "model"
        )

        vectorizer = model_data.get(
            "vectorizer"
        )

    else:

        model = model_data
        vectorizer = None

    if model is None:
        raise ValueError(
            "Invalid ML model file."
        )

    # --------------------------------------------------------
    # Find description column
    # --------------------------------------------------------

    description_column = None

    for column in transactions_df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
        )

        if normalized in [
            "description",
            "merchant",
            "transaction description",
            "merchant / description",
        ]:

            description_column = column
            break

    if description_column is None:

        raise ValueError(
            "No transaction description column found."
        )

    descriptions = (
        transactions_df[
            description_column
        ]
        .fillna("")
        .astype(str)
    )

    # --------------------------------------------------------
    # Transform text
    # --------------------------------------------------------

    if vectorizer is not None:

        features = vectorizer.transform(
            descriptions
        )

    else:

        features = descriptions

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    predictions = model.predict(
        features
    )

    result = transactions_df.copy()

    result[
        "ML Category"
    ] = predictions

    return result