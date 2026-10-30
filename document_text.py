from pathlib import Path
from io import BytesIO
import os
import shutil

import pymupdf
import pytesseract
from PIL import Image


# Find Tesseract on Windows or Linux.
# On Render/Linux, Tesseract will be installed through Docker.
# On Windows, use the default installation path if available.

tesseract_path = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")

if not tesseract_path:
    windows_path = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if windows_path.exists():
        tesseract_path = str(windows_path)

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


def get_document_text(file_path):
    """
    Read text from TXT, normal PDF, scanned PDF, PNG, and JPG files.

    This function only extracts text.
    It does not save data to MySQL.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Use TXT, PDF, PNG, or JPG."
        )

    # Read plain text files directly.
    if extension == ".txt":
        return path.read_text(encoding="utf-8-sig")

    # Read images using OCR.
    if extension in {".png", ".jpg", ".jpeg"}:
        with Image.open(path) as image:
            return pytesseract.image_to_string(
                image,
                lang="eng",
            )

    # For PDFs, try normal text extraction first.
    # Use OCR on pages with almost no extractable text.
    page_texts = []

    with pymupdf.open(path) as document:
        for page in document:
            text = page.get_text("text")

            if len(text.strip()) < 20:
                pixmap = page.get_pixmap(
                    dpi=300,
                    alpha=False,
                )

                png_bytes = pixmap.tobytes("png")

                with Image.open(BytesIO(png_bytes)) as image:
                    text = pytesseract.image_to_string(
                        image,
                        lang="eng",
                    )

            page_texts.append(text)

    return "\n".join(page_texts)