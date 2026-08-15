from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from src.processor import process_statement


# ============================================================
# PDF TO TEST
# ============================================================

pdf_path = Path(
    r"C:\Users\LEVONO\Downloads\synthetic_statement_20260815_115023_5698.pdf"
)


# ============================================================
# CHECK FILE
# ============================================================

if not pdf_path.exists():

    print("=" * 70)
    print("PDF NOT FOUND")
    print("=" * 70)

    print(
        f"\nExpected file:\n{pdf_path}"
    )

    print(
        "\nGenerate a dummy statement first."
    )

    sys.exit(1)


# ============================================================
# PROCESS
# ============================================================

print("=" * 70)
print("END-TO-END PIPELINE TEST")
print("=" * 70)

print(
    f"\nUsing PDF:\n{pdf_path}"
)

try:

    df = process_statement(
        str(pdf_path)
    )

except Exception as error:

    print("\nPIPELINE FAILED")
    print(error)

    raise


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("FINAL TRANSACTION DATA")
print("=" * 70)

print(
    df.to_string(
        index=False
    )
)

print("\n" + "=" * 70)

print(
    f"Transactions extracted: {len(df)}"
)

print(
    f"Categories found: "
    f"{df['Category'].nunique()}"
)

print("\nCategory distribution:")

print(
    df["Category"].value_counts()
)

print("\nPIPELINE TEST PASSED")

print("=" * 70)