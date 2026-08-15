from pathlib import Path

import pandas as pd

from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

SOURCE_FILE = DATA_DIR / "labeled_transactions.csv"

TRAIN_FILE = DATA_DIR / "train_transactions.csv"

TEST_FILE = DATA_DIR / "test_transactions.csv"


# ============================================================
# SPLIT DATASET
# ============================================================

def split_dataset():

    print("=" * 70)
    print("TRANSACTION DATASET SPLITTING")
    print("=" * 70)


    # --------------------------------------------------------
    # Check source dataset
    # --------------------------------------------------------

    if not SOURCE_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {SOURCE_FILE}"
        )


    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(
        SOURCE_FILE
    )


    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    required_columns = {
        "description",
        "category"
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            f"Missing columns: {missing_columns}"
        )


    # --------------------------------------------------------
    # Remove empty rows
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "description",
            "category"
        ]
    )


    df["description"] = (
        df["description"]
        .astype(str)
        .str.strip()
    )


    df["category"] = (
        df["category"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Display original dataset
    # --------------------------------------------------------

    print(
        f"\nTotal transactions: {len(df)}"
    )

    print(
        f"Total categories: "
        f"{df['category'].nunique()}"
    )


    print(
        "\nOriginal category distribution:"
    )

    print(
        df["category"].value_counts()
    )


    # --------------------------------------------------------
    # STRATIFIED TRAIN / TEST SPLIT
    # --------------------------------------------------------

    train_df, test_df = train_test_split(

        df,

        test_size=0.20,

        random_state=42,

        stratify=df["category"]
    )


    # --------------------------------------------------------
    # Shuffle datasets
    # --------------------------------------------------------

    train_df = train_df.sample(
        frac=1,
        random_state=42
    ).reset_index(
        drop=True
    )


    test_df = test_df.sample(
        frac=1,
        random_state=42
    ).reset_index(
        drop=True
    )


    # --------------------------------------------------------
    # Save datasets
    # --------------------------------------------------------

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    train_df.to_csv(
        TRAIN_FILE,
        index=False
    )


    test_df.to_csv(
        TEST_FILE,
        index=False
    )


    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print(
        f"\nTraining samples: {len(train_df)}"
    )

    print(
        f"Testing samples: {len(test_df)}"
    )


    print(
        "\nTraining distribution:"
    )

    print(
        train_df["category"].value_counts()
    )


    print(
        "\nTesting distribution:"
    )

    print(
        test_df["category"].value_counts()
    )


    print(
        "\nFiles created:"
    )

    print(
        TRAIN_FILE
    )

    print(
        TEST_FILE
    )


    print("=" * 70)


if __name__ == "__main__":

    split_dataset()