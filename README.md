# Invoice Data Extractor

## About the Project

I created this project to extract information from invoices using Python and OCR.

The application can read TXT files, normal PDFs, scanned PDFs and invoice images. It extracts the invoice details and displays them on a React page.

Users can check the extracted information, correct any mistakes and save the final data in a MySQL database. The changes made by the user are also saved in a correction log.

## Features

- Upload TXT, PDF, PNG and JPG files.
- Extract text from normal PDFs.
- Read scanned PDFs and images using Tesseract OCR.
- Extract vendor name, invoice number, invoice date and GSTIN.
- Extract taxable amount and GST details.
- Check whether the invoice total matches the amount and GST.
- View extracted details on the frontend.
- Edit incorrect or missing values.
- Save invoice details in MySQL.
- Store corrected fields in a correction log.
- Display error messages for unsupported, empty or unreadable files.

## Technologies Used

- Python
- FastAPI
- Uvicorn
- PyMuPDF
- Tesseract OCR
- pytesseract
- Pillow
- python-dotenv
- React
- Vite
- HTML and CSS
- MySQL

## Requirements

Before running the project, install:

- Python
- Node.js and npm
- MySQL Server
- MySQL Workbench
- Tesseract OCR
- VS Code (optional)

## How to Run the Project

### 1. Get the Project

Open the project folder in VS Code and open a terminal in the main project directory.

### 2. Set Up Python

Create a virtual environment:

```bash
python -m venv .venv
```

For Windows Command Prompt, activate it using:

```cmd
.venv\Scripts\activate.bat
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

### 3. Set Up Tesseract OCR

Install Tesseract OCR on your computer.

Installing pytesseract using pip does not install the Tesseract application itself.

In my current setup, Tesseract is installed at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If it is installed in another location, update the path in `document_text.py`.

### 4. Set Up MySQL

Start MySQL Server and open MySQL Workbench.

Create the database and tables using the provided `schema.sql` file.

Create a `.env` file in the main project folder and add your own database connection details:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=invoice_db
```

Replace the example password with your own MySQL password.

Do not upload your `.env` file to GitHub.

### 5. Run the Backend

Activate the Python environment and run this command from the main project folder:

```bash
python -m uvicorn main:app --reload
```

The backend runs at:

http://127.0.0.1:8000

To view the API documentation, open:

http://127.0.0.1:8000/docs

Keep the backend terminal running.

### 6. Run the Frontend

Open another terminal in VS Code.

Move to the frontend folder:

```bash
cd frontend
```

Install the frontend packages:

```bash
npm ci
```

Start the React application:

```bash
npm run dev
```

Open the URL shown in the terminal. It is usually:

http://localhost:5173/

Keep both backend and frontend running while using the application.

## How the Application Works

1. Select an invoice file.
2. Upload the file through the frontend.
3. The backend reads the invoice text or uses OCR when needed.
4. The application extracts the invoice details.
5. Check the extracted information.
6. Correct any incorrect values.
7. Save the invoice.
8. The invoice data and corrections are stored in MySQL.

## Testing

I tested the application using different sample invoice files.

The test files include:

- TXT invoices
- Normal PDF invoices
- Scanned PDF invoices
- PNG invoice images
- Different invoice layouts
- CGST and SGST invoices
- IGST invoices

To test document text extraction:

```bash
python test_document_text.py
```

Other available test files are:

```bash
python test_corrections.py
python test_save_corrections.py
python test_save_invoice.py
python test_save_invoice_with_corrections.py
```

To check the MySQL connection:

```bash
python test_db_connection.py
```

To test an invoice separately:

```bash
python -c "from invoice_extractor import extract_invoice; print(extract_invoice('docs/sample_invoice_02.pdf'))"
```

Additional test invoices are available in:

```text
docs/unseen_invoice_tests/
```

I also tested invoice editing and saving through the frontend. The invoice details and corrections were successfully saved and checked in MySQL.

## Limitations

- Extraction results depend on the quality of the invoice.
- Blurry images can cause missing or incorrect values.
- Different invoice layouts may need additional extraction rules.
- Users should check the extracted information before saving.
- The current total validation checks taxable amount plus GST. Invoices with additional charges or round-off differences may need extra handling.
- The project has been tested using fictional sample invoices. Its accuracy on real-world invoices has not yet been established.

## Current Project Status

The main extraction, frontend and database features are implemented.

I tested the application with the available sample invoices, including different invoice layouts, PDFs and images.

The application currently runs locally on my computer. More work is needed before using it in a production environment.

For future deployment, authentication, access control and secure hosting configuration will also be needed.

## Security

- Do not upload `.env` files.
- Do not share database passwords.
- Keep database credentials in local environment variables.
- Do not upload private credentials to GitHub.
- Review the project configuration before deployment.