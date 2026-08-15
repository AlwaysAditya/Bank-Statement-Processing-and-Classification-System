from pathlib import Path
import sys


# Allow Python to find the src folder
sys.path.append(
    str(Path(__file__).resolve().parents[1])
)


from src.text_processor import (
    extract_text_from_pdf,
    extract_tables_from_pdf
)


# ============================================================
# CONFIGURATION
# ============================================================

DOWNLOADS_FOLDER = Path.home() / "Downloads"


# ============================================================
# FIND PDFs
# ============================================================

pdf_files = list(
    DOWNLOADS_FOLDER.glob("*.pdf")
)


if not pdf_files:

    print("No PDF files found in Downloads.")
    print(
        f"Checked: {DOWNLOADS_FOLDER}"
    )

    sys.exit(1)


# ============================================================
# TEST
# ============================================================

print("=" * 70)
print("TEXT PROCESSOR TEST")
print("=" * 70)


for pdf_file in pdf_files:

    print("\n" + "-" * 70)

    print(
        f"File: {pdf_file.name}"
    )

    # --------------------------------------------------------
    # TEXT EXTRACTION
    # --------------------------------------------------------

    try:

        result = extract_text_from_pdf(
            pdf_file
        )

        print(
            f"Pages: {result['page_count']}"
        )

        print(
            f"Characters extracted: "
            f"{len(result['full_text'])}"
        )

        print("\n--- FIRST 1000 CHARACTERS ---")

        print(
            result["full_text"][:1000]
        )

    except Exception as e:

        print(
            f"TEXT EXTRACTION ERROR: {e}"
        )


    # --------------------------------------------------------
    # TABLE EXTRACTION
    # --------------------------------------------------------

    try:

        table_result = extract_tables_from_pdf(
            pdf_file
        )

        total_tables = 0

        for page in table_result["pages"]:

            total_tables += len(
                page["tables"]
            )

        print(
            f"\nTables found: {total_tables}"
        )

    except Exception as e:

        print(
            f"TABLE EXTRACTION ERROR: {e}"
        )


print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)