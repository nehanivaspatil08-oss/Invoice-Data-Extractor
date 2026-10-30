
import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const detailFields = [
  { key: "vendor_name", label: "Vendor name", type: "text" },
  { key: "invoice_number", label: "Invoice number", type: "text" },
  { key: "invoice_date", label: "Invoice date", type: "text" },
  { key: "gstin", label: "GSTIN", type: "text" },
];

const amountFields = [
  { key: "amount_before_gst", label: "Amount before GST" },
  { key: "cgst", label: "CGST" },
  { key: "sgst", label: "SGST" },
  { key: "igst", label: "IGST" },
  { key: "total_gst", label: "Total GST" },
  { key: "total_amount", label: "Grand total", emphasized: true },
];

const allFields = [...detailFields, ...amountFields];

const currencyFields = new Set(
  amountFields.map((field) => field.key)
);

function sameValue(first, second) {
  return String(first ?? "").trim() === String(second ?? "").trim();
}

function App() {
  const [file, setFile] = useState(null);
  const [originalData, setOriginalData] = useState(null);
  const [editedData, setEditedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [fileInputKey, setFileInputKey] = useState(0);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const changedFields =
    originalData && editedData
      ? allFields.filter(
          (field) =>
            !sameValue(
              originalData[field.key],
              editedData[field.key]
            )
        )
      : [];

  function selectFile(selectedFile) {
    if (!selectedFile) return;

    setFile(selectedFile);
    setOriginalData(null);
    setEditedData(null);
    setError("");
    setMessage("");
  }

  async function extractInvoice() {
    if (!file) {
      setError("Choose an invoice file before continuing.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setOriginalData(null);
    setEditedData(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/extract-invoice`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Unable to extract this invoice."
        );
      }

      setOriginalData(result);
      setEditedData({ ...result });
      setMessage("Review the extracted information before saving.");
    } catch (err) {
      setError(
        err.message || "Unable to connect to the invoice API."
      );
    } finally {
      setLoading(false);
    }
  }

  function updateField(key, value) {
    setEditedData((previous) => ({
      ...previous,
      [key]: value,
    }));

    setMessage("");
    setError("");
  }

  async function saveInvoice() {
    if (!originalData || !editedData) {
      setError("Extract an invoice before saving.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    const correctedData = { ...editedData };

    for (const field of allFields) {
      const value = correctedData[field.key];

      if (typeof value === "string" && value.trim() === "") {
        correctedData[field.key] = null;
      } else if (
        currencyFields.has(field.key) &&
        value !== null &&
        value !== undefined
      ) {
        const numberValue = Number(value);

        if (!Number.isFinite(numberValue)) {
          setError(`Enter a valid amount for ${field.label}.`);
          setSaving(false);
          return;
        }

        correctedData[field.key] = numberValue;
      }
    }

    try {
      const response = await fetch(`${API_URL}/save-invoice`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          original_data: originalData,
          corrected_data: correctedData,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Unable to save the invoice."
        );
      }

      setMessage(
        `Invoice saved successfully. Invoice ID: ${result.invoice_id}. Corrections logged: ${result.corrections_saved}.`
      );
    } catch (err) {
      setError(err.message || "Unable to save the invoice.");
    } finally {
      setSaving(false);
    }
  }

  function uploadAnother() {
    setFile(null);
    setOriginalData(null);
    setEditedData(null);
    setError("");
    setMessage("");
    setFileInputKey((previous) => previous + 1);
  }

  function renderField(field) {
    const value = editedData[field.key] ?? "";

    const isEdited = !sameValue(
      originalData[field.key],
      editedData[field.key]
    );

    const igstPresent =
      editedData.igst !== null &&
      editedData.igst !== undefined &&
      String(editedData.igst).trim() !== "" &&
      Number(editedData.igst) > 0;

    const localTaxPresent = ["cgst", "sgst"].some(
      (key) =>
        editedData[key] !== null &&
        editedData[key] !== undefined &&
        String(editedData[key]).trim() !== "" &&
        Number(editedData[key]) > 0
    );

    const notApplicable =
      (["cgst", "sgst"].includes(field.key) && igstPresent) ||
      (field.key === "igst" && localTaxPresent);

    const isMissing =
      !notApplicable && String(value).trim() === "";

    return (
      <label
        className={`field-group ${
          isMissing ? "field-missing" : ""
        } ${field.key === "vendor_name" ? "field-full" : ""}`}
        key={field.key}
      >
        <span className="field-label-row">
          <span>{field.label}</span>
          {isEdited && <span className="edited-tag">Edited</span>}
        </span>

        <span
          className={`input-wrap ${
            notApplicable ? "not-applicable-wrap" : ""
          }`}
        >
          {currencyFields.has(field.key) && !notApplicable && (
            <span className="currency-prefix">₹</span>
          )}

          <input
            type={
              notApplicable
                ? "text"
                : currencyFields.has(field.key)
                  ? "number"
                  : "text"
            }
            step={
              currencyFields.has(field.key) && !notApplicable
                ? "any"
                : undefined
            }
            className={
              notApplicable
                ? "not-applicable-input"
                : currencyFields.has(field.key)
                  ? "amount-input"
                  : ""
            }
            value={notApplicable ? "Not applicable" : value}
            readOnly={notApplicable}
            onChange={(event) =>
              updateField(field.key, event.target.value)
            }
            placeholder={
              notApplicable
                ? ""
                : isMissing
                  ? "Not found — enter value"
                  : `Enter ${field.label.toLowerCase()}`
            }
          />
        </span>

        {isMissing && (
          <span className="missing-hint">
            Please check this field.
          </span>
        )}
      </label>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">ID</div>
          <div>
            <h1>Invoice Data Extractor</h1>
            <p>Invoice processing workspace</p>
          </div>
        </div>

        <div className="topbar-status">
          <span className="status-dot" />
          Local application
        </div>
      </header>

      <section className="page-intro">
        <div>
          <p className="eyebrow">INVOICE MANAGEMENT</p>
          <h2>Review invoices with confidence.</h2>
          <p className="intro-description">
            Extract invoice details, review the results, correct
            mistakes and save verified information.
          </p>
        </div>
      </section>

      <section className="panel upload-panel">
        <div className="section-heading">
          <div className="section-title-group">
            <span className="step-number">01</span>
            <div>
              <h3>Upload invoice</h3>
              <p>Start by selecting a document to process.</p>
            </div>
          </div>

          <span className="file-type-hint">PDF · TXT · PNG · JPG</span>
        </div>

        <label
          className={`upload-dropzone ${
            dragActive ? "drag-active" : ""
          }`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragActive(false);
            selectFile(event.dataTransfer.files?.[0]);
          }}
        >
          {/* IMPORTANT: this is the file picker, not an invoice field. */}
          <input
            key={fileInputKey}
            type="file"
            accept=".pdf,.txt,.png,.jpg,.jpeg"
            onChange={(event) =>
              selectFile(event.target.files?.[0])
            }
          />

          <span className="upload-icon">
            <svg
              viewBox="0 0 24 24"
              width="25"
              height="25"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M12 16V4" />
              <path d="m7 9 5-5 5 5" />
              <path d="M4 16.5v2A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5v-2" />
            </svg>
          </span>

          <strong>
            {file ? file.name : "Drop your invoice here"}
          </strong>

          <span className="upload-subtext">
            {file
              ? "File selected. Ready to extract."
              : "Drag and drop a file, or click to browse"}
          </span>

          <span className="browse-label">Choose file</span>
          <span className="file-limit">Maximum file size: 10 MB</span>
        </label>

        <div className="upload-actions">
          <span className="privacy-hint">
            <span className="privacy-symbol">✓</span>
            Review extracted values before saving.
          </span>

          <button
            className="primary-button"
            onClick={extractInvoice}
            disabled={!file || loading}
          >
            {loading && <span className="spinner" />}
            {loading ? "Reading invoice..." : "Extract invoice data"}
          </button>
        </div>
      </section>

      {error && (
        <div className="notice error-notice" role="alert">
          <span className="notice-icon">!</span>
          <div>
            <strong>Unable to process invoice</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {message && (
        <div className="notice success-notice" role="status">
          <span className="notice-icon">✓</span>
          <div>
            <strong>
              {message.startsWith("Invoice saved")
                ? "Invoice saved"
                : "Ready for review"}
            </strong>
            <p>{message}</p>
          </div>
        </div>
      )}

      {editedData && (
        <section className="review-section">
          <div className="review-heading">
            <div className="section-title-group">
              <span className="step-number">02</span>
              <div>
                <h3>Review and correct</h3>
                <p>Check the extracted values against your invoice.</p>
              </div>
            </div>

            <div
              className={`validation-badge ${String(
                editedData.validation_status || "SKIP"
              ).toLowerCase()}`}
            >
              <span className="validation-icon">
                {editedData.validation_status === "PASS"
                  ? "✓"
                  : editedData.validation_status === "FAIL"
                    ? "!"
                    : "–"}
              </span>

              <span>
                <strong>
                  {editedData.validation_status || "SKIP"}
                </strong>
                <small>
                  {editedData.validation_status === "PASS"
                    ? "Amounts add up"
                    : editedData.validation_status === "FAIL"
                      ? "Check the amounts"
                      : "Unable to validate"}
                </small>
              </span>
            </div>
          </div>

          <div className="review-grid">
            <section className="panel review-card">
              <div className="card-heading">
                <span className="card-icon details-icon">▤</span>
                <div>
                  <h4>Invoice details</h4>
                  <p>Supplier and document information</p>
                </div>
              </div>

              <div className="detail-fields">
                {detailFields.map(renderField)}
              </div>
            </section>

            <section className="panel review-card">
              <div className="card-heading">
                <span className="card-icon amount-icon">₹</span>
                <div>
                  <h4>Invoice amounts</h4>
                  <p>Tax breakdown and final amount</p>
                </div>
              </div>

              <div className="amount-fields">
                {amountFields.map(renderField)}
              </div>
            </section>
          </div>

          <div className="review-action-bar">
            <div className="change-summary">
              <span className="change-count">
                {changedFields.length}
              </span>

              <div>
                <strong>
                  {changedFields.length === 1
                    ? "Field changed"
                    : "Fields changed"}
                </strong>
                <span>
                  {changedFields.length === 0
                    ? "No manual corrections yet"
                    : "Changes will be recorded"}
                </span>
              </div>
            </div>

            <div className="action-buttons">
              <button
                className="secondary-button"
                onClick={uploadAnother}
                disabled={saving}
              >
                Upload another
              </button>

              <button
                className="primary-button save-button"
                onClick={saveInvoice}
                disabled={saving}
              >
                {saving && <span className="spinner" />}
                {saving ? "Saving invoice..." : "Save invoice"}
              </button>
            </div>
          </div>
        </section>
      )}

      <footer className="app-footer">
        <span>Invoice Data Extractor</span>
        <span>Python · FastAPI · React · MySQL</span>
      </footer>
    </main>
  );
}

export default App;
