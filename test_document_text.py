
from document_text import get_document_text

test_files = [
    "docs/sample_invoice_02.txt",
    "docs/sample_invoice_02.pdf",
    "docs/sample_invoice_02_ocr_test.png",
]

for file_path in test_files:
    print("\n" + "=" * 55)
    print("Testing:", file_path)

    try:
        text = get_document_text(file_path)

        print("Text extraction successful.")
        print("First 500 characters:")
        print(text[:500])

        if not text.strip():
            print("WARNING: No text was extracted.")

    except Exception as error:
        print("TEST FAILED:", error)
