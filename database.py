import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "invoice_db")
    )



def save_invoice(invoice_data):
    connection = None
    cursor = None

    query = """
        INSERT INTO invoices (
            vendor_name,
            invoice_number,
            invoice_date,
            amount_before_gst,
            cgst,
            sgst,
            igst,
            total_gst,
            total_amount,
            gstin,
            validation_status
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """

    values = (
        invoice_data.get("vendor_name"),
        invoice_data.get("invoice_number"),
        invoice_data.get("invoice_date"),
        invoice_data.get("amount_before_gst"),
        invoice_data.get("cgst"),
        invoice_data.get("sgst"),
        invoice_data.get("igst"),
        invoice_data.get("total_gst"),
        invoice_data.get("total_amount"),
        invoice_data.get("gstin"),
        invoice_data.get("validation_status", "SKIP"),
    )

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()

        return cursor.lastrowid

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def save_corrections(invoice_id, changes):
    if not changes:
        return 0

    query = """
        INSERT INTO correction_log (
            invoice_id,
            field_name,
            original_value,
            corrected_value
        )
        VALUES (%s, %s, %s, %s)
    """

    values = [
        (
            invoice_id,
            change["field_name"],
            (
                str(change["original_value"])
                if change["original_value"] is not None
                else None
            ),
            (
                str(change["corrected_value"])
                if change["corrected_value"] is not None
                else None
            ),
        )
        for change in changes
    ]

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.executemany(query, values)
        connection.commit()

        return cursor.rowcount

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def save_invoice_with_corrections(invoice_data, changes):
    connection = None
    cursor = None

    invoice_query = """
        INSERT INTO invoices (
            vendor_name,
            invoice_number,
            invoice_date,
            amount_before_gst,
            cgst,
            sgst,
            igst,
            total_gst,
            total_amount,
            gstin,
            validation_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    correction_query = """
        INSERT INTO correction_log (
            invoice_id,
            field_name,
            original_value,
            corrected_value
        )
        VALUES (%s, %s, %s, %s)
    """

    invoice_values = (
        invoice_data.get("vendor_name"),
        invoice_data.get("invoice_number"),
        invoice_data.get("invoice_date"),
        invoice_data.get("amount_before_gst"),
        invoice_data.get("cgst"),
        invoice_data.get("sgst"),
        invoice_data.get("igst"),
        invoice_data.get("total_gst"),
        invoice_data.get("total_amount"),
        invoice_data.get("gstin"),
        invoice_data.get("validation_status", "SKIP"),
    )

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Save the final invoice.
        cursor.execute(invoice_query, invoice_values)
        invoice_id = cursor.lastrowid

        # Save all corrections linked to this invoice.
        if changes:
            correction_values = [
                (
                    invoice_id,
                    change["field_name"],
                    (
                        str(change["original_value"])
                        if change["original_value"] is not None
                        else None
                    ),
                    (
                        str(change["corrected_value"])
                        if change["corrected_value"] is not None
                        else None
                    ),
                )
                for change in changes
            ]

            cursor.executemany(correction_query, correction_values)

        # Commit both operations together.
        connection.commit()

        return invoice_id, len(changes)

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
