
CREATE DATABASE IF NOT EXISTS invoice_db;

USE invoice_db;


-- Stores the final saved invoice data
CREATE TABLE IF NOT EXISTS invoices (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    vendor_name VARCHAR(255) NULL,
    invoice_number VARCHAR(100) NULL,
    invoice_date DATE NULL,

    amount_before_gst DECIMAL(12,2) NULL,
    cgst DECIMAL(12,2) NULL,
    sgst DECIMAL(12,2) NULL,
    igst DECIMAL(12,2) NULL,
    total_gst DECIMAL(12,2) NULL,
    total_amount DECIMAL(12,2) NULL,

    gstin VARCHAR(20) NULL,
    validation_status VARCHAR(10) NOT NULL DEFAULT 'SKIP',

    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Records changes made by users
CREATE TABLE IF NOT EXISTS correction_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    invoice_id BIGINT UNSIGNED NOT NULL,
    field_name VARCHAR(100) NOT NULL,

    original_value TEXT NULL,
    corrected_value TEXT NULL,

    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_correction_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
        ON DELETE CASCADE
);
