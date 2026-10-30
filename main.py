from pathlib import Path
import os
import tempfile

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    Body,
)
from fastapi.middleware.cors import CORSMiddleware

from invoice_extractor import extract_invoice
from corrections import find_corrections
from database import save_invoice_with_corrections


app = FastAPI(
    title="Invoice Data Extractor API",
    description="Extract invoice data from TXT, PDF and image files.",
    version="1.0.0",
)


# Allow local frontend and deployed Vercel frontend.
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_origin = os.getenv("FRONTEND_ORIGIN", "")

if frontend_origin:
    allowed_origins.extend(
        origin.strip()
        for origin in frontend_origin.split(",")
        if origin.strip()
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Invoice Data Extractor API is running"
    }


@app.post("/extract-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an invoice file.",
        )

    suffix = Path(file.filename).suffix.lower()

    if suffix not in [".txt", ".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=400,
            detail="Only TXT, PDF, PNG, JPG and JPEG files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 10 MB.",
        )

    temporary_path = None

    try:
        # Save the uploaded file temporarily for extraction.
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = temporary_file.name

        # Extract invoice fields from the uploaded document.
        invoice_data = extract_invoice(temporary_path)

        # Reject documents where no important fields were extracted.
        important_fields = (
            "vendor_name",
            "invoice_number",
            "invoice_date",
            "amount_before_gst",
            "total_amount",
            "gstin",
        )

        if not any(
            invoice_data.get(field)
            for field in important_fields
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Could not read enough invoice details. "
                    "Please upload a clearer image or PDF."
                ),
            )

        return invoice_data

    except HTTPException:
        raise

    except (ValueError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=422,
            detail=f"Could not process invoice: {error}",
        ) from error

    except Exception as error:
        print("Invoice extraction error:", error)

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred while processing "
                "the invoice."
            ),
        ) from error

    finally:
        # Always remove the temporary upload.
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


@app.post("/save-invoice")
def save_invoice_endpoint(payload: dict = Body(...)):
    original_data = payload.get("original_data")
    corrected_data = payload.get("corrected_data")

    if (
        not isinstance(original_data, dict)
        or not isinstance(corrected_data, dict)
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Both original_data and corrected_data "
                "must be provided."
            ),
        )

    try:
        changes = find_corrections(
            original_data,
            corrected_data,
        )

        invoice_id, corrections_saved = (
            save_invoice_with_corrections(
                corrected_data,
                changes,
            )
        )

        return {
            "message": "Invoice and corrections saved successfully",
            "invoice_id": invoice_id,
            "corrections_saved": corrections_saved,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print("Invoice save error:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to save invoice and corrections.",
        ) from error