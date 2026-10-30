from document_text import get_document_text

test_files = [
    "docs/sample_invoice_02_ocr_test.png",
    "docs/sample_invoice_blurry.jpg",
    "docs/sample_invoice_photo.png",
    "docs/sample_scanned_invoice.pdf",
]

for file_path in test_files:
    print("\n" + "=" * 55)
    print("Testing:", file_path)

    try:
        text = get_document_text(file_path)

        if text.strip():
            print("Text extraction successful.")
            print("First 500 characters:")
            print(text[:500])
        else:
            print("WARNING: No text was extracted.")

    except Exception as error:
        print("TEST FAILED:", error)