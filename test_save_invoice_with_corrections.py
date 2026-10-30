
from corrections import find_corrections
from database import save_invoice_with_corrections

original_invoice = {
    "vendor_name": "Western Office Solutions",
    "invoice_number": "WOS/2026/025",
    "invoice_date": "2026-11-12",
    "amount_before_gst": 125000.00,
    "cgst": None,
    "sgst": None,
    "igst": 22500.00,
    "total_gst": 22500.00,
    "total_amount": 147500.00,
    "gstin": "27PQRSX5678L1Z2",
    "validation_status": "PASS",
}

corrected_invoice = original_invoice.copy()
corrected_invoice["invoice_number"] = "WOS/2026/026"
corrected_invoice["gstin"] = "27PQRSX5678L1Z3"

changes = find_corrections(original_invoice, corrected_invoice)

try:
    invoice_id, saved_count = save_invoice_with_corrections(
        corrected_invoice,
        changes,
    )

    print("Invoice and corrections saved successfully!")
    print("Invoice ID:", invoice_id)
    print("Corrections saved:", saved_count)

except Exception as error:
    print("Save failed.")
    print("Error:", error)
