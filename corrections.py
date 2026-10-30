
from decimal import Decimal, InvalidOperation

FIELDS_TO_COMPARE = [
    "vendor_name",
    "invoice_number",
    "invoice_date",
    "amount_before_gst",
    "cgst",
    "sgst",
    "igst",
    "total_gst",
    "total_amount",
    "gstin",
]

MONEY_FIELDS = {
    "amount_before_gst",
    "cgst",
    "sgst",
    "igst",
    "total_gst",
    "total_amount",
}


def normalize_value(field_name, value):
    # Treat None, empty strings, and spaces as missing values.
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

    # Compare money values numerically, up to two decimal places.
    if field_name in MONEY_FIELDS:
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError(
                f"Invalid number for {field_name}: {value!r}"
            )

    # Trim extra spaces from text fields.
    return value


def find_corrections(original_data, corrected_data):
    changes = []

    for field_name in FIELDS_TO_COMPARE:
        original_value = original_data.get(field_name)
        corrected_value = corrected_data.get(field_name)

        normalized_original = normalize_value(
            field_name, original_value
        )
        normalized_corrected = normalize_value(
            field_name, corrected_value
        )

        if normalized_original != normalized_corrected:
            changes.append({
                "field_name": field_name,
                "original_value": original_value,
                "corrected_value": corrected_value,
            })

    return changes
