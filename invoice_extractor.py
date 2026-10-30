
import re
from pathlib import Path
from datetime import datetime

from document_text import get_document_text


# Common number and currency patterns.
NUMBER_PATTERN = r"-?\d[\d,]*(?:\.\d+)?"

CURRENCY_PATTERN = re.compile(
    r"(?:\bINR\b|Rs\.?|₹)\s*([0-9][\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)

AMOUNT_ONLY_PATTERN = re.compile(
    rf"^(?:(?:INR\b|Rs\.?|₹)\s*)?{NUMBER_PATTERN}$",
    re.IGNORECASE,
)

TAX_LABELS = {
    "cgst",
    "sgst",
    "igst",
    "integrated gst",
}


def clean_line(line):
    """Remove leading OCR punctuation and extra whitespace."""
    return line.strip().lstrip("‘'\"`|;").strip()


def normalize_date(value):
    """Convert supported invoice dates to YYYY-MM-DD."""
    if value is None:
        return None

    value = value.strip()

    date_formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y",
    )

    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(value, date_format)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Preserve unrecognised dates for manual review.
    return value


def looks_like_field_label(line):
    """Identify known labels when searching subsequent lines."""
    known_labels = (
        "vendor name",
        "supplier",
        "seller name",
        "invoice number",
        "invoice no",
        "bill no",
        "reference number",
        "invoice ref",
        "invoice date",
        "bill date",
        "gstin",
        "gst registration",
        "gst registration number",
        "amount before gst",
        "taxable value after discount",
        "net taxable value",
        "cgst",
        "sgst",
        "igst",
        "integrated gst",
        "total gst",
        "total tax",
        "gst total",
        "grand total",
        "net payable",
        "total payable",
    )

    return any(
        re.match(
            rf"^{re.escape(label)}\b",
            line.strip(),
            re.IGNORECASE,
        )
        for label in known_labels
    )


def has_amount(value):
    """Check for a tax amount rather than a percentage alone."""
    if not value:
        return False

    if CURRENCY_PATTERN.search(value):
        return True

    if "%" in value:
        after_rate = value.split("%", 1)[1]
        return bool(re.search(NUMBER_PATTERN, after_rate))

    return bool(re.search(NUMBER_PATTERN, value))


def find_field(lines, labels):
    """Find a labelled field and support values on subsequent lines."""

    for index, line in enumerate(lines):
        text = clean_line(line)

        for label in labels:
            label_text = label.rstrip(":").strip()

            label_pattern = r"\s+".join(
                re.escape(part)
                for part in label_text.split()
            )

            match = re.match(
                rf"^{label_pattern}\s*[:=;：]*\s*(.*)$",
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            # Assign the captured value before cleaning it.
            value = match.group(1).strip()

            # Remove leading punctuation without removing hyphens
            # inside invoice numbers such as NOM-6107.
            value = re.sub(
                r"^[\s:;=|.,]+",
                "",
                value,
            ).strip()

            # Keep a vendor name separate from a GSTIN that OCR
            # may put on the same line.
            if label_text.lower() in {
                "vendor name",
                "supplier",
                "seller name",
            }:
                value = re.split(
                    r"\s+(?:GSTIN|GST Registration(?: Number)?)\b",
                    value,
                    maxsplit=1,
                    flags=re.IGNORECASE,
                )[0].strip()

            # Tax labels may show the rate first and the amount
            # on a later line.
            if label_text.lower() in TAX_LABELS:
                if has_amount(value):
                    return value

                if value.lower() in {
                    "not applicable",
                    "n/a",
                    "na",
                    "-",
                }:
                    return value

                # Search subsequent lines. OCR can place the
                # taxable-value line between the tax rate and amount.
                for next_line in lines[index + 1:]:
                    candidate = clean_line(next_line)

                    if not candidate:
                        continue

                    candidate_lower = candidate.lower()

                    # Skip taxable-value lines rather than stopping.
                    if any(
                        term in candidate_lower
                        for term in (
                            "amount before gst",
                            "taxable value",
                            "net taxable value",
                        )
                    ):
                        continue

                    # Do not accidentally read the grand total
                    # as a GST component.
                    if any(
                        term in candidate_lower
                        for term in (
                            "grand total",
                            "net payable",
                            "total payable",
                            "total gst",
                            "total tax",
                            "gst total",
                        )
                    ):
                        break

                    if looks_like_field_label(candidate):
                        break

                    if AMOUNT_ONLY_PATTERN.fullmatch(candidate):
                        return candidate

                    amount_match = CURRENCY_PATTERN.search(candidate)

                    if amount_match:
                        return amount_match.group(0)

                if value:
                    return value

                continue

            if value:
                return value

            # If a normal field's value is on the next line,
            # do not consume another labelled field accidentally.
            for next_line in lines[index + 1:]:
                candidate = clean_line(next_line)

                if not candidate:
                    continue

                if looks_like_field_label(candidate):
                    break

                return candidate

    # OCR sometimes recognises the GSTIN but misses its label.
    if any(
        label.rstrip(":").strip().lower() in {
            "gstin",
            "gst registration",
            "gst registration number",
        }
        for label in labels
    ):
        for line in lines:
            match = re.search(
                r"\b\d{2}[A-Z0-9]{13}\b",
                line.upper(),
            )

            if match:
                return match.group(0)

    return None


def to_number(value):
    """Convert currency text or tax lines into numeric amounts."""
    if value is None:
        return None

    value = str(value).strip()

    # Prefer values explicitly marked with INR, Rs. or ₹.
    currency_match = CURRENCY_PATTERN.search(value)

    if currency_match:
        return float(
            currency_match.group(1).replace(",", "")
        )

    # For "@ 9% 1,620.00", return 1620 rather than the rate 9.
    if "%" in value:
        after_rate = value.split("%", 1)[1]

        numbers_after_rate = re.findall(
            NUMBER_PATTERN,
            after_rate,
        )

        if numbers_after_rate:
            return float(
                numbers_after_rate[-1].replace(",", "")
            )

        # Only the percentage was found; no amount was detected.
        return None

    value = value.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", value)

    if not match:
        return None

    return float(match.group(0))


def extract_invoice(file_path):
    """Extract invoice fields and validate the GST total."""

    invoice_path = Path(file_path)

    if not invoice_path.exists():
        raise FileNotFoundError(
            f"Invoice file not found: {invoice_path}"
        )

    # Supports TXT, normal/scanned PDFs, PNG and JPG through OCR
    # and document text extraction.
    invoice_text = get_document_text(invoice_path)
    lines = invoice_text.splitlines()

    vendor_name = find_field(
        lines,
        [
            "Vendor Name",
            "Supplier",
            "Seller Name",
        ],
    )

    invoice_number = find_field(
        lines,
        [
            "Invoice Number",
            "Invoice No",
            "Bill No",
            "Reference Number",
            "Invoice Ref",
        ],
    )

    invoice_date = normalize_date(
        find_field(
            lines,
            [
                "Invoice Date",
                "Bill Date",
            ],
        )
    )

    amount_before_gst = to_number(
        find_field(
            lines,
            [
                "Amount Before GST",
                "Taxable value after discount",
                "Net taxable value",
            ],
        )
    )

    cgst = to_number(
        find_field(lines, ["CGST"])
    )

    sgst = to_number(
        find_field(lines, ["SGST"])
    )

    igst = to_number(
        find_field(
            lines,
            [
                "IGST",
                "Integrated GST",
            ],
        )
    )

    total_gst = to_number(
        find_field(
            lines,
            [
                "Total GST",
                "Total tax",
                "GST total",
            ],
        )
    )

    # Derive total GST if only the individual tax components exist.
    if total_gst is None:
        if igst is not None:
            total_gst = igst
        elif cgst is not None or sgst is not None:
            total_gst = (cgst or 0) + (sgst or 0)

    total_amount = to_number(
        find_field(
            lines,
            [
                "Grand Total",
                "Net payable",
                "Total payable",
            ],
        )
    )

    gstin = find_field(
        lines,
        [
            "GSTIN",
            "GST Registration Number",
            "GST Registration",
        ],
    )

    validation_status = "SKIP"

    # Compare amounts only when all required values are available.
    if (
        amount_before_gst is not None
        and total_gst is not None
        and total_amount is not None
    ):
        calculated_total = round(
            amount_before_gst + total_gst,
            2,
        )

        if calculated_total == round(total_amount, 2):
            validation_status = "PASS"
        else:
            validation_status = "FAIL"

    return {
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
        "validation_status": validation_status,
    }
