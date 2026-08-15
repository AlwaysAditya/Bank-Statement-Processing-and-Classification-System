from pathlib import Path
import pytesseract


image_path = Path(__file__).parent / "test_image.png"


print("=" * 60)
print("TESSERACT OCR TEST")
print("=" * 60)

print(f"Image: {image_path}")

if not image_path.exists():
    print("ERROR: test_image.png not found.")
    raise SystemExit(1)


text = pytesseract.image_to_string(
    str(image_path)
)


print("\n--- EXTRACTED TEXT ---")
print(text)

print("=" * 60)
print("OCR TEST COMPLETED")
print("=" * 60)