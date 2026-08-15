from pathlib import Path
import sys

# Allow Python to find the src folder
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pdf_detector import detect_pdf_type


# ============================================================
# CONFIGURATION
# ============================================================

DOWNLOADS_FOLDER = Path.home() / "Downloads"


# ============================================================
# FIND PDF FILES
# ============================================================

pdf_files = list(DOWNLOADS_FOLDER.glob("*.pdf"))


if not pdf_files:
    print("No PDF files found in Downloads.")
    print(f"Checked: {DOWNLOADS_FOLDER}")
    sys.exit(1)


# ============================================================
# TEST ALL PDFs
# ============================================================

print("=" * 70)
print("PDF DETECTOR TEST")
print("=" * 70)

for pdf_file in pdf_files:

    try:
        result = detect_pdf_type(pdf_file)

        print(f"\nFile : {pdf_file.name}")
        print(f"Type : {result}")

    except Exception as e:

        print(f"\nFile : {pdf_file.name}")
        print(f"ERROR: {e}")


print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)