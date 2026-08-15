from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

import pandas as pd

from src.classifier import (
    classify_transaction,
    classify_transactions,
)


# ============================================================
# TEST INDIVIDUAL TRANSACTIONS
# ============================================================

test_cases = {

    "Amazon": "Shopping",

    "Zomato": "Food & Dining",

    "Uber": "Transport",

    "DMart": "Groceries",

    "Airtel": "Utilities",

    "Netflix": "Entertainment",

    "Apollo Pharmacy": "Healthcare",

    "LIC": "Insurance",

    "SBI Mutual Fund": "Investments",

    "IRCTC": "Travel & Booking",

    "SALARY CREDIT": "Income",

    "AMAZON REFUND": "Refund / Cashback",

    "UNKNOWN MERCHANT": "Other",
}


print("=" * 70)
print("CLASSIFIER TEST")
print("=" * 70)


passed = 0
failed = 0


for description, expected in test_cases.items():

    predicted = classify_transaction(
        description
    )

    status = (
        "PASS"
        if predicted == expected
        else "FAIL"
    )

    print(
        f"{status:<6} "
        f"{description:<25} "
        f"Expected: {expected:<20} "
        f"Predicted: {predicted}"
    )

    if predicted == expected:
        passed += 1
    else:
        failed += 1


# ============================================================
# DATAFRAME TEST
# ============================================================

df = pd.DataFrame({
    "Date": [
        "01/01/2026",
        "02/01/2026",
        "03/01/2026",
    ],

    "Description": [
        "Amazon",
        "Uber",
        "SALARY CREDIT",
    ],

    "Debit": [
        2500,
        500,
        None,
    ],

    "Credit": [
        None,
        None,
        60000,
    ],

    "Balance": [
        50000,
        49500,
        109500,
    ],
})


classified_df = classify_transactions(
    df
)


print("\n" + "=" * 70)
print("DATAFRAME CLASSIFICATION")
print("=" * 70)

print(
    classified_df.to_string(
        index=False
    )
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
)

if failed == 0:

    print("\nALL CLASSIFIER TESTS PASSED")

else:

    print(
        "\nSOME CLASSIFIER TESTS FAILED"
    )

print("=" * 70)