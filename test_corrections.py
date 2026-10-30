
from corrections import find_corrections

original = {
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


def check_case(name, original_data, corrected_data, expected_count):
    changes = find_corrections(original_data, corrected_data)
    passed = len(changes) == expected_count

    print(f"{name}: {'PASS' if passed else 'FAIL'}")

    if not passed:
        print("Expected changes:", expected_count)
        print("Actual changes:", changes)

    return passed


results = []

# 1. Nothing changed
results.append(check_case(
    "Test 1 - No changes",
    original,
    original.copy(),
    0
))

# 2. Invoice number changed
data = original.copy()
data["invoice_number"] = "WOS/2026/026"
results.append(check_case(
    "Test 2 - Invoice number changed",
    original, data, 1
))

# 3. Missing IGST was filled in
data = original.copy()
data["igst"] = None
updated = data.copy()
updated["igst"] = 22500
results.append(check_case(
    "Test 3 - Missing IGST filled",
    data, updated, 1
))

# 4. Same amount, different format
data = original.copy()
updated = original.copy()
data["igst"] = 22500.0
updated["igst"] = "22500.00"
results.append(check_case(
    "Test 4 - Same amount format",
    data, updated, 0
))

# 5. None and empty string mean the same
data = original.copy()
updated = original.copy()
data["gstin"] = None
updated["gstin"] = ""
results.append(check_case(
    "Test 5 - Empty GSTIN",
    data, updated, 0
))

# 6. Extra spaces should not count as a change
data = original.copy()
updated = original.copy()
data["vendor_name"] = "Western Office Solutions"
updated["vendor_name"] = "  Western Office Solutions  "
results.append(check_case(
    "Test 6 - Extra spaces",
    data, updated, 0
))

# 7. Existing total amount was cleared
data = original.copy()
updated = original.copy()
updated["total_amount"] = None
results.append(check_case(
    "Test 7 - Total amount cleared",
    data, updated, 1
))

# 8. Only validation status changed
data = original.copy()
updated = original.copy()
updated["validation_status"] = "PASS"
data["validation_status"] = "FAIL"
results.append(check_case(
    "Test 8 - Validation status ignored",
    data, updated, 0
))

# 9. Three fields changed
updated = original.copy()
updated["invoice_number"] = "WOS/2026/026"
updated["igst"] = 23000
updated["gstin"] = "27NEWGSTIN1234X1Z"
changes = find_corrections(original, updated)

passed = (
    len(changes) == 3
    and {change["field_name"] for change in changes}
    == {"invoice_number", "igst", "gstin"}
)
print(f"Test 9 - Three fields changed: {'PASS' if passed else 'FAIL'}")
results.append(passed)

print(f"\nTotal passed: {sum(results)}/9")
