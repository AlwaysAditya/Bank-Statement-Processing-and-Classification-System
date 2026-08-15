from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

import pandas as pd

from src.validator import (
    validate_transactions
)


# ============================================================
# TEST DATA
# ============================================================

data = {
    "Date": pd.to_datetime([
        "2026-01-01",
        "2026-01-02",
        "2026-01-03",
    ]),

    "Description": [
        "Amazon",
        "Uber",
        "SALARY CREDIT",
    ],

    "Debit": [
        2500.00,
        450.00,
        None,
    ],

    "Credit": [
        None,
        None,
        60000.00,
    ],

    "Balance": [
        50000.00,
        49550.00,
        109550.00,
    ],
}


df = pd.DataFrame(data)


# ============================================================
# VALIDATE
# ============================================================

cleaned_df, results = validate_transactions(
    df
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 60)
print("VALIDATOR TEST")
print("=" * 60)

print("\nValidation Results:")

for key, value in results.items():

    print(
        f"{key}: {value}"
    )


print("\nTransactions:")

print(
    cleaned_df.to_string(
        index=False
    )
)

print("\n" + "=" * 60)

if results["valid"]:

    print("TEST PASSED")

else:

    print("TEST FAILED")

print("=" * 60)