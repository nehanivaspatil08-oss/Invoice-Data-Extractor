
from pathlib import Path
from datetime import datetime
import json
import pymupdf


# Select invoice file
invoice_path = Path(input("Enter invoice file path: "))

if not invoice_path.exists():
    print("Error: Invoice file not found. Please check the file path.")
    exit()
if invoice_path.suffix.lower() == ".pdf":
    document = pymupdf.open(invoice_path)
    invoice_text = "\n".join(
        page.get_text() for page in document
    )
    document.close()
else:
    invoice_text = invoice_path.read_text(encoding="utf-8")


# Find a field using possible labels
def find_field(lines, labels):
    for line in lines:
        for label in labels:
            if line.lower().startswith(label.lower()):
                return line.split(":", 1)[1].strip()

    return None


# Convert currency text into a number
def to_number(value):
    if value is None:
        return None

    value = value.replace("Rs.", "")
    value = value.replace("₹", "")
    value = value.replace(",", "")
    value = value.strip()

    return float(value)


lines = invoice_text.splitlines()

print(invoice_text)


# Extract vendor name
vendor_name = find_field(lines, ["Vendor Name:"])
print("\n--- Extracted Vendor ---")
print(vendor_name)


# Extract invoice number
invoice_number = find_field(
    lines,
    ["Invoice Number:", "Invoice No:", "Bill No."]
)
print("\n--- Extracted Invoice Number ---")
print(invoice_number)


# Extract invoice date
invoice_date = find_field(lines, ["Invoice Date:"])

if invoice_date is not None:
    invoice_date = datetime.strptime(
        invoice_date, "%d/%m/%Y"
    ).strftime("%Y-%m-%d")

print("\n--- Extracted Invoice Date ---")
print(invoice_date)


# Extract amount before GST
amount_before_gst = to_number(
    find_field(lines, ["Amount Before GST:"])
)
print("\n--- Amount Before GST ---")
print(amount_before_gst)


# Extract CGST
cgst = to_number(find_field(lines, ["CGST"]))
print("\n--- Extracted CGST ---")
print(cgst)


# Extract SGST
sgst = to_number(find_field(lines, ["SGST"]))
print("\n--- Extracted SGST ---")
print(sgst)


# Extract IGST
igst = to_number(find_field(lines, ["IGST"]))
print("\n--- Extracted IGST ---")
print(igst)


# Extract total GST if available.
# Otherwise calculate it from the available tax fields.
total_gst = to_number(find_field(lines, ["Total GST:"]))

if total_gst is None:
    if igst is not None:
        total_gst = igst
    elif cgst is not None or sgst is not None:
        total_gst = (cgst or 0) + (sgst or 0)

print("\n--- Extracted Total GST ---")
print(total_gst)


# Extract grand total
total_amount = to_number(find_field(lines, ["Grand Total:"]))
print("\n--- Extracted Grand Total ---")
print(total_amount)


# Extract GSTIN
gstin = find_field(lines, ["GSTIN:"])
print("\n--- Extracted GSTIN ---")
print(gstin)


# Validate invoice amounts BEFORE building invoice_data
print("\n--- Invoice Amount Validation ---")

validation_status = "SKIP"

if (
    amount_before_gst is not None
    and total_gst is not None
    and total_amount is not None
):
    calculated_total = round(amount_before_gst + total_gst, 2)

    if calculated_total == round(total_amount, 2):
        validation_status = "PASS"
        print("PASS: Invoice amounts match.")
    else:
        validation_status = "FAIL"
        print("FAIL: Invoice amounts do not match.")
        print("Calculated Total:", calculated_total)
        print("Invoice Grand Total:", total_amount)
else:
    print("SKIP: Required amount fields are missing.")


# Build final invoice data
invoice_data = {
    "vendor_name": vendor_name,
    "invoice_number": invoice_number,
    "invoice_date": invoice_date,
    "amount_before_gst": amount_before_gst,
    "cgst": cgst,
    "sgst": sgst,
    "igst": igst,
    "total_gst": total_gst,
    "total_amount": total_amount,
    "gstin": gstin,
    "validation_status": validation_status
}


# Print final JSON
print("\n--- Final JSON Output ---")
print(json.dumps(invoice_data, indent=4))


# Save JSON output
output_path = Path("invoice_output.json")

output_path.write_text(
    json.dumps(invoice_data, indent=4),
    encoding="utf-8"
)

print(f"\nJSON saved to: {output_path.resolve()}")
