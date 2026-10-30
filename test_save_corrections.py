
from database import save_corrections

test_changes = [
    {
        "field_name": "igst",
        "original_value": 22500,
        "corrected_value": 23000,
    },
    {
        "field_name": "invoice_number",
        "original_value": "WOS/2026/025",
        "corrected_value": "WOS/2026/026",
    },
]

try:
    saved_count = save_corrections(3, test_changes)
    print("Correction log saved successfully!")
    print("Number of corrections saved:", saved_count)

except Exception as error:
    print("Correction log save failed.")
    print("Error:", error)
