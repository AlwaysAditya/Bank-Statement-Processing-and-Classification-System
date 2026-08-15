from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

TRAIN_FILE = DATA_DIR / "train_transactions.csv"
TEST_FILE = DATA_DIR / "test_transactions.csv"

VECTORIZER_FILE = MODEL_DIR / "tfidf_vectorizer.joblib"
MODEL_FILE = MODEL_DIR / "transaction_classifier.joblib"


# ============================================================
# LOAD DATA
# ============================================================

def load_datasets():

    if not TRAIN_FILE.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {TRAIN_FILE}"
        )

    if not TEST_FILE.exists():
        raise FileNotFoundError(
            f"Testing dataset not found: {TEST_FILE}"
        )

    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    required_columns = {
        "description",
        "category"
    }

    for name, df in [
        ("training", train_df),
        ("testing", test_df)
    ]:

        missing = required_columns - set(df.columns)

        if missing:
            raise ValueError(
                f"{name.title()} dataset missing columns: {missing}"
            )

    return train_df, test_df


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    print("=" * 70)
    print("TRANSACTION CLASSIFICATION MODEL")
    print("=" * 70)

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    train_df, test_df = load_datasets()

    print(
        f"\nTraining samples: {len(train_df)}"
    )

    print(
        f"Testing samples: {len(test_df)}"
    )

    # --------------------------------------------------------
    # Training data
    # --------------------------------------------------------

    X_train = (
        train_df["description"]
        .astype(str)
    )

    y_train = (
        train_df["category"]
        .astype(str)
    )

    # --------------------------------------------------------
    # Testing data
    # --------------------------------------------------------

    X_test = (
        test_df["description"]
        .astype(str)
    )

    y_test = (
        test_df["category"]
        .astype(str)
    )

    # ========================================================
    # TF-IDF
    # ========================================================

    print("\nCreating TF-IDF features...")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    X_train_tfidf = vectorizer.fit_transform(
        X_train
    )

    X_test_tfidf = vectorizer.transform(
        X_test
    )

    print(
        f"Training feature matrix: "
        f"{X_train_tfidf.shape}"
    )

    print(
        f"Testing feature matrix: "
        f"{X_test_tfidf.shape}"
    )

    # ========================================================
    # LOGISTIC REGRESSION
    # ========================================================

    print("\nTraining Logistic Regression...")

    model = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    model.fit(
        X_train_tfidf,
        y_train
    )

    # ========================================================
    # EVALUATION
    # ========================================================

    print("\nEvaluating model...")

    predictions = model.predict(
        X_test_tfidf
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_FILE
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print("\nModel saved:")

    print(
        VECTORIZER_FILE
    )

    print(
        MODEL_FILE
    )

    print("=" * 70)

    return model, vectorizer


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

def load_model():

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            "Trained classifier not found. "
            "Run: python -m src.ml_classifier"
        )

    if not VECTORIZER_FILE.exists():

        raise FileNotFoundError(
            "TF-IDF vectorizer not found. "
            "Run: python -m src.ml_classifier"
        )

    model = joblib.load(
        MODEL_FILE
    )

    vectorizer = joblib.load(
        VECTORIZER_FILE
    )

    return model, vectorizer


# ============================================================
# PREDICT TRANSACTION
# ============================================================

def predict_transaction(
    description,
    confidence_threshold=0.50
):

    model, vectorizer = load_model()

    description = str(
        description
    )

    features = vectorizer.transform(
        [description]
    )

    probabilities = model.predict_proba(
        features
    )[0]

    predicted_index = probabilities.argmax()

    predicted_category = (
        model.classes_[predicted_index]
    )

    confidence = probabilities[
        predicted_index
    ]

    # --------------------------------------------------------
    # Low confidence
    # --------------------------------------------------------

    if confidence < confidence_threshold:

        return (
            "Other",
            float(confidence)
        )

    return (
        predicted_category,
        float(confidence)
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    train_model()