# Claude Log

I am keeping these notes to remember what I asked Claude, what it suggested, what I learned, and what I changed in my Invoice Data Extractor project.

## 26 October 2026 — Understanding the assignment

### What I asked Claude

I explained that I had been given an Invoice Data Extractor assignment. I know basic Python and SQL, but I am new to building a complete application. I asked Claude to explain the assignment in simple English and help me decide what to build first. I asked it not to write code yet.

### What Claude suggested

Claude explained that the project has three main parts:

1. Read invoice PDFs and images using text extraction, OCR and rules.
2. Build a React page where a user can check and correct the extracted values, then save them to a database.
3. If there is enough time, compare the rule-based approach with a pretrained document model.

Claude suggested starting with extraction before moving to the frontend and database.

### What I learned

I learned that I should build the project in small steps. First, I needed to read invoice text and identify the required fields. After that, I could connect the API, frontend and database.

## 27 October 2026 — Making a sample invoice

### What I discussed with Claude

I asked what I should do next before starting the extraction code.

### What Claude suggested

Claude suggested creating a fictional sample invoice and keeping it in the project's `docs` folder. It also explained that I should write down the correct values so I can compare them with the values returned by my code.

### What I learned

A sample invoice with known answers makes testing easier. I can check each field instead of guessing whether the extraction result is correct.

### What I decided

I started with fictional invoice data so I would not need to use real customer or business information.

## 29 October 2026 — Improving the frontend design

### What I asked Claude

The basic frontend was working, but it looked too simple. I asked Claude to review the progress and suggest a more professional layout. I asked it not to write code until I had reviewed the design, and I said I did not want to break the existing backend, OCR or MySQL features.

### What Claude suggested

Claude recommended keeping the design simple and consistent instead of adding lots of effects. It suggested:

- One main colour, with a light background and white cards.
- A clear upload area showing the selected file and loading or error messages.
- Separate cards for invoice details and invoice amounts.
- A clear validation status.
- A marker for fields I had edited.
- Save and upload-another buttons, with a clear success message.
- Using plain CSS and not adding new UI libraries.
- Making small changes and testing after each one.

Claude also advised me to save a Git commit before changing the UI and to work on a separate branch.

### What I decided and changed

I checked Git, created a repository in my project folder, committed the working version and created the `ui-redesign` branch. My baseline commit was `ca501ea`.

I updated `frontend/src/index.css`, `frontend/src/App.jsx` and `frontend/src/App.css`. I kept the existing API addresses and the field keys used by the backend. During the changes, I accidentally put an invoice-field input in the upload section, which caused a white page. I checked the browser console, found the `notApplicable is not defined` error, and corrected the misplaced input. After that, the page opened again.

I tested extraction and saving through the redesigned UI. Invoice ID 12 was saved, and MySQL showed that the correction log recorded this change:

`WOS/2026/025` -> `WOS/2026/025-UITEST`

The frontend showed that one correction was logged. I then committed the UI changes as `c8fcbb2` with the message `Polish invoice extractor UI`.

### What I learned

I learned that a browser console error can help find the reason for a white page. I also learned why it is useful to keep a Git commit before changing working code.

## 29 October 2026 — Testing new invoice layouts

### What I asked Claude

I gave Claude an update about the working OCR, API, MySQL saving, correction log, error handling and new UI. I asked what I should do next and asked it to help me choose the most important remaining task.

### What Claude suggested

Claude said that the main features were in place, but the tests so far mostly used sample invoices that I had prepared. It recommended trying invoice layouts that were not used while building the extraction rules. It also said I should not claim a real-world accuracy figure until I had tested more independent invoices.

Claude highlighted a possible problem with reading tax amounts: an extractor can pick the tax rate, such as 9%, instead of the actual tax amount. It recommended checking these cases before making more changes.

### What I decided

I decided to start with two new fictional text invoices instead of collecting invoices from other people straight away. I saved them in `docs/unseen_invoice_tests/`:

- `test_invoice_01.txt` uses labels such as `Supplier`, `Reference Number`, `Bill Date`, `Taxable value after discount`, and `Net payable`. It has CGST and SGST.
- `test_invoice_02.txt` uses labels such as `Seller Name`, `Invoice Ref`, `Net taxable value`, `Integrated GST`, and `Total payable`. It uses an `INR` amount format and IGST.

### What happened in the first tests

The first runs showed that the old extraction rules missed several new labels. The CGST and SGST fields also returned `9.0` instead of the tax amount of `1620.0`. This helped me see the difference between a tax rate and the amount charged.

### What I changed

I updated `invoice_extractor.py` to recognise more field labels, handle more date formats, and read amounts with `INR`, `Rs.` or `₹`. I also updated the tax-line search because the OCR text for my PNG put the `Amount Before GST` line between the IGST label and the IGST amount. At first, this made IGST return `None`; after changing the search to skip the taxable-value line, the PNG test passed again.

I also fixed extra punctuation at the start of an invoice number extracted from a PDF. I kept the output field names and the validation result structure the same.

### Results after the changes

The following tests returned the expected values and `Validation: PASS`:

- `docs/unseen_invoice_tests/test_invoice_01.txt`
- `docs/unseen_invoice_tests/test_invoice_02.txt`
- `docs/sample_invoice_02.txt`
- `docs/sample_invoice_02.pdf`
- `docs/sample_invoice_photo.png`
- `docs/sample_scanned_invoice.pdf`

I ran `python test_document_text.py`. Text extraction worked for the sample TXT, PDF and OCR test PNG.

These are useful results, but the two new invoices are still fictional test cases that I created. I have not yet measured accuracy on a wider set of independent real-world layouts.

### Git update

I ran `git diff --check`; it returned no output. I committed `invoice_extractor.py` and the two new test invoices with this commit:

- Commit: `f5097df`
- Message: `Improve invoice extraction for varied formats`

After the commit, `git status` showed a clean working tree on `ui-redesign`.

## 29 October 2026 — Clean setup test

### What I wanted to check

I wanted to see whether the project could run in a new Python environment, instead of relying only on the environment I had used while developing it.

### What I did

I created a temporary environment named `invoice-clean-test` and installed the packages from `requirements.txt`. `python -m pip check` returned `No broken requirements found.`

In this new environment, I successfully extracted:

- `test_invoice_01.txt`
- `sample_invoice_photo.png`
- `sample_scanned_invoice.pdf`

The output values were as expected and validation returned `PASS` for these sample files.

I then ran `npm ci` in the `frontend` folder. The first attempt failed with a Windows `EPERM` error because a frontend native file appeared to be in use. After stopping the running React server and trying again, `npm ci` completed successfully and reported zero vulnerabilities. `npm run build` also completed successfully (`built in 185ms`).

I started FastAPI from the temporary Python environment. Uvicorn started at `http://127.0.0.1:8000` and showed `Application startup complete.`

### What I learned

A clean environment is a useful check because it shows whether the project depends on packages that happen to be installed only in my original environment. I also learned that Windows can prevent a package file from being replaced while a development server is using it.

### What is still pending

I have not yet finished checking the API through Swagger while using the clean environment, and I have not yet completed a full frontend-to-backend run from a fresh setup. I still need to review the README steps against what I actually did.

## Current status and next steps

The current Git branch is `ui-redesign`. The latest commit is `f5097df`, and the last Git status check was clean.

The main extraction flow, the redesigned UI, MySQL saving, and correction logging have been tested with fictional sample data. More testing is still needed before making claims about general accuracy.

My next tasks are:

1. Finish the clean-setup API check and confirm the README instructions.
2. Run a final end-to-end test of upload, extraction, edit, save, and correction logging.
3. Prepare a simple report with the test cases, results, and current limitations.
4. Only consider the optional pretrained-model comparison if the required work is finished and there is enough time.
