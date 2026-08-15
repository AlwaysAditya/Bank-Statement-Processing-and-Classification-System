Bank Statement Processing & Classification System

A Python + Streamlit prototype that processes bank statement PDFs, extracts transaction data from both text-based and image-based PDFs, classifies transactions without using LLMs, and exports the results to CSV/Excel.

Live Demo: [Bank Statement Processing & Classification System](https://bank-statement-processing-and-classification-system.streamlit.app/)

1. Features
Upload bank statement PDFs through Streamlit.
Automatically detect:
Text-based PDFs
Image/scanned PDFs
Process text PDFs using PDF text extraction.
Process scanned PDFs using OCR.
Extract:
Date
Transaction description
Debit
Credit
Balance
Extract account/statement information.
Classify transactions without LLMs.
Rule-based transaction classification.
Traditional ML classification using TF-IDF + classifier.
Handle unknown transactions using Other.
Export processed transactions to:
CSV
Excel
Generate synthetic bank statements for testing.
Support multiple pages in PDF statements.
2. Architecture
                    BANK STATEMENT PDF
                           │
                           ▼
                   ┌─────────────────┐
                   │  PDF Detector   │
                   └────────┬────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
            TEXT PDF              IMAGE PDF
                 │                     │
                 ▼                     ▼
        Text Processor           OCR Processor
                 │                     │
                 └──────────┬──────────┘
                            ▼
                  Transaction Extractor
                            │
                            ▼
                       Validator
                            │
                            ▼
                     Classification
                     ┌──────┴──────┐
                     │             │
                   Rules       ML Model
                     │             │
                     └──────┬──────┘
                            ▼
                     Classified Data
                            │
                     ┌──────┴──────┐
                     ▼             ▼
                    CSV          Excel

The architecture intentionally separates PDF detection, extraction, validation and classification so individual components can be improved independently.

3. Tech Stack
Technology	Purpose
Python	Core application and processing
Streamlit	Web UI
Pandas	Data processing and DataFrames
PyMuPDF	PDF reading and text extraction
Pytesseract	OCR for scanned/image PDFs
Pillow	Image processing for OCR
scikit-learn	Traditional ML classification
TF-IDF	Convert transaction descriptions into numerical features
Joblib	Save/load trained ML models
OpenPyXL	Excel export
ReportLab	Synthetic PDF generation
Regex	Pattern matching and transaction extraction
Git	Version control
GitHub	Source-code repository
VS Code	Development environment
4. Project Structure
Bank Statement Processing and Classification System/
│
├── app.py
├── dummy_statement_generator.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── labeled_transactions.csv
│   ├── train_transactions.csv
│   └── test_transactions.csv
│
├── models/
│   ├── tfidf_vectorizer.joblib
│   └── transaction_classifier.joblib
│
├── src/
│   ├── account_extractor.py
│   ├── classifier.py
│   ├── classifier_engine.py
│   ├── ml_classifier.py
│   ├── ocr_processor.py
│   ├── pdf_detector.py
│   ├── processor.py
│   ├── split_dataset.py
│   ├── text_processor.py
│   ├── transaction_extractor.py
│   └── validator.py
│
└── tests/
    └── ...
5. Processing Pipeline
Step 1 — PDF Upload

The user uploads a bank statement PDF through the Streamlit interface.

Step 2 — PDF Type Detection

pdf_detector.py determines whether the document contains extractable text or requires OCR.

Step 3 — Text Processing

For text-based PDFs:

PDF → PyMuPDF → Extracted Text
Step 4 — OCR Processing

For scanned/image PDFs:

PDF → Page Images → Tesseract OCR → Extracted Text
Step 5 — Transaction Extraction

transaction_extractor.py converts extracted text into a structured DataFrame:

Date
Description
Debit
Credit
Balance
Step 6 — Validation

validator.py checks whether the extracted transaction data satisfies the expected structure and contains valid transactions.

Step 7 — Classification

Transactions are classified using non-LLM techniques.

The classification layer supports:

Transaction Description
        │
        ▼
Rule-Based Classification
        │
        ├── Match → Category
        │
        └── No Match
                │
                ▼
          ML Classifier
                │
                ▼
             Category
Step 8 — Export

The final classified DataFrame can be exported as:

CSV
Excel (.xlsx)
6. Transaction Categories

The classifier supports categories such as:

Groceries
Food & Dining
Transport
Utilities
Shopping
Entertainment
Healthcare
Insurance
Investments
Travel & Booking
Income
Refund / Cashback
Other

The classification system is designed so additional categories and merchant rules can be added without changing the extraction pipeline.

7. Non-LLM Classification

The assessment specifically requires transaction classification without relying on LLMs.

This implementation therefore uses traditional approaches:

Rule-Based Classification

Transaction descriptions are normalized and matched against predefined merchant/keyword patterns.

Example:

Amazon
    ↓
Shopping


Uber
    ↓
Transport


Zomato
    ↓
Food & Dining


SALARY CREDIT
    ↓
Income
Machine Learning

The ML pipeline uses:

Transaction Description
        ↓
Text preprocessing
        ↓
TF-IDF Vectorization
        ↓
Traditional ML Classifier
        ↓
Predicted Category

The trained components are stored using Joblib:

models/
├── tfidf_vectorizer.joblib
└── transaction_classifier.joblib
8. Synthetic Test Data

The project includes a synthetic bank statement generator:

dummy_statement_generator.py

It creates fictional bank statements containing:

Random bank names
Random customer names
Synthetic account IDs
Synthetic transaction references
Random dates
Multiple transactions
Debit/credit transactions
Real-world merchant names
Multi-page statements

Generated statements are intended for testing purposes only and do not contain real customer financial information.

9. Running Locally
Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "Bank Statement Processing and Classification System"
Create virtual environment
python -m venv venv
Activate

Windows Git Bash:

source venv/Scripts/activate

Windows PowerShell:

venv\Scripts\Activate.ps1
Install dependencies
pip install -r requirements.txt
Run Streamlit
streamlit run app.py

The application will open at:

http://localhost:8501
10. OCR Setup

Image-based PDF processing requires Tesseract OCR.

Install Tesseract and ensure the executable is available in the system PATH.

Verify the installation:

tesseract --version

Verify Python integration:

python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
11. Testing

The project contains separate tests for individual components and the complete processing pipeline.

Example:

python tests/test_classifier.py

End-to-end testing:

python tests/test_pipeline.py

The recommended testing flow is:

Synthetic PDF
     ↓
PDF Detector
     ↓
Text/OCR Processor
     ↓
Transaction Extraction
     ↓
Validation
     ↓
Classification
     ↓
Export
12. Edge Cases Considered

The prototype is designed with common bank-statement variations in mind:

Text-based PDFs
Scanned/image PDFs
Multi-page statements
Empty debit cells
Empty credit cells
Comma-formatted amounts
Different transaction descriptions
Income transactions
Refund/cashback transactions
Unknown merchants
Missing/invalid transaction rows
Different bank names and layouts
OCR-based extraction errors
13. Limitations

This is a prototype, not a production banking-data ingestion system.

Current limitations include:

Bank layouts vary significantly and may require bank-specific parsing rules.
OCR accuracy depends on document quality.
Complex tables may require additional layout-aware extraction.
Transaction classification accuracy depends on available training data and rules.
Account-detail extraction may require additional bank-specific patterns.
Password-protected/encrypted PDFs may require additional handling.
14. Future Improvements

Potential production-level enhancements:

Bank-specific extraction profiles.
Better table extraction using PDF coordinates/layout information.
Improved OCR preprocessing.
Confidence scores for extracted fields and classifications.
Human-in-the-loop correction.
Automatic model retraining from corrected classifications.
Duplicate transaction detection.
Balance reconciliation.
Password-protected PDF support.
More extensive automated test coverage.
Logging and monitoring.
API-based processing service.
Database-backed processing history.
Authentication and role-based access control.
15. Security & Privacy

This prototype is designed to process bank statements without using an LLM for transaction classification.

For production deployment, additional security controls should be implemented, including:

Encryption at rest and in transit
Secure temporary-file handling
PII masking
Access control
Audit logging
Automatic deletion of uploaded documents
Secure secrets management

Do not upload real bank statements containing sensitive financial information to the public demo. Use synthetic/test statements instead.

16. Assessment Alignment
Assessment Requirement	Implementation
PDF input	Streamlit PDF upload
Text PDFs	Text processing pipeline
Image PDFs	Tesseract OCR pipeline
Multiple pages	Page-wise processing
Account information	Account extraction module
Date	Transaction extractor
Description	Transaction extractor
Debit	Transaction extractor
Credit	Transaction extractor
Balance	Transaction extractor
Non-LLM classification	Rule-based + traditional ML
Excel output	OpenPyXL
CSV output	Pandas
Edge cases	Validation + extraction handling
Extensible architecture	Modular src/ components
Prototype UI	Streamlit
17. Author

Aditya Salani

AI Automation / Data Science Project

Built as a prototype for demonstrating:

Document processing
OCR
Python automation
Data extraction
Rule-based classification
Traditional machine learning
Streamlit application development
Data export