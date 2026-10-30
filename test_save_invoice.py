
from database import save_invoice

sample_invoice = {
    "vendor_name": "Test Supplier",
    "invoice_number": "TEST-001",
    "invoice_date": "2026-10-28",
    "amount_before_gst": 1000.00,
    "cgst": 90.00,
    "sgst": 90.00,
    "igst": None,
    "total_gst": 180.00,
    "total_amount": 1180.00,
    "gstin": "27ABCDE1234F1Z5",
    "validation_status": "PASS"
}

try:
    invoice_id = save_invoice(sample_invoice)
    print("Invoice saved successfully!")
    print("Invoice ID:", invoice_id)
except Exception as error:
    print("Invoice save failed.")
    print("Error:", error)
