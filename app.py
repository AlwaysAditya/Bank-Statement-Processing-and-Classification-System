import os
import tempfile
from io import BytesIO
import re

import fitz
import pandas as pd
import streamlit as st

from src.processor import process_statement
from dummy_statement_generator import create_random_statement


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bank Statement Processor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN APP
       ======================================================== */

    .main {
        padding-top: 1rem;
    }

    .app-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }


    /* ========================================================
       DARK SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #111827 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #f9fafb !important;
    }

    section[data-testid="stSidebar"] p {
        color: #f9fafb !important;
    }

    section[data-testid="stSidebar"] span {
        color: #f9fafb !important;
    }

    section[data-testid="stSidebar"] label {
        color: #f9fafb !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #374151 !important;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: #d1d5db !important;
    }

    section[data-testid="stSidebar"] button {
        background-color: #1f2937 !important;
        color: #f9fafb !important;
        border: 1px solid #374151 !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: #374151 !important;
        color: white !important;
        border-color: #6b7280 !important;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .workflow-box {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px;
        padding: 11px 12px;
        margin-bottom: 7px;
    }

    .workflow-number {
        color: #93c5fd !important;
        font-weight: 700;
    }

    .workflow-text {
        color: #f9fafb !important;
        font-weight: 500;
    }

    .workflow-arrow {
        text-align: center;
        color: #9ca3af !important;
        font-size: 18px;
        margin: 1px 0;
    }


    /* ========================================================
       ACCOUNT INFORMATION
       ======================================================== */

    .account-value-box {
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        color: #111827;
        font-weight: 600;
        min-height: 42px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

if "account_details" not in st.session_state:
    st.session_state.account_details = {}

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False


# ============================================================
# CLEAR APPLICATION
# ============================================================

def clear_application():

    st.session_state.processed_df = None
    st.session_state.account_details = {}
    st.session_state.uploaded_filename = None
    st.session_state.processing_complete = False


# ============================================================
# ACCOUNT DETAILS EXTRACTION
# ============================================================

def extract_account_details(pdf_path):
    """
    Extract account-level information directly from the PDF.

    Expected fields:

        Bank Name
        Customer
        Account Number
        IFSC Code
        Branch / City
        Statement Period

    This is intentionally independent from process_statement().
    """

    details = {
        "account_holder": "Not detected",
        "account_number": "Not detected",
        "bank_name": "Not detected",
        "ifsc": "Not detected",
        "branch": "Not detected",
        "statement_period": "Not detected",
    }

    try:

        document = fitz.open(pdf_path)

        pages_text = []

        for page in document:

            text = page.get_text("text")

            if text:
                pages_text.append(text)

        document.close()

        full_text = "\n".join(pages_text)

        if not full_text.strip():
            return details

        text = full_text.replace("\r", "\n")

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]


        # ====================================================
        # GENERIC LABEL/VALUE EXTRACTOR
        # ====================================================

        def get_value_from_lines(labels):

            for i, line in enumerate(lines):

                clean_line = line.strip()
                lower_line = clean_line.lower()

                for label in labels:

                    label_lower = label.lower()

                    # ----------------------------------------
                    # Label: Value
                    # ----------------------------------------

                    if lower_line.startswith(
                        label_lower + ":"
                    ):

                        value = clean_line[
                            len(label) + 1:
                        ].strip()

                        if value:
                            return value


                    # ----------------------------------------
                    # Label - Value
                    # ----------------------------------------

                    if lower_line.startswith(
                        label_lower + " -"
                    ):

                        value = clean_line[
                            len(label) + 2:
                        ].strip()

                        if value:
                            return value


                    # ----------------------------------------
                    # Label on one line
                    # Value on next line
                    # ----------------------------------------

                    if lower_line == label_lower:

                        if i + 1 < len(lines):

                            next_line = (
                                lines[i + 1].strip()
                            )

                            if next_line:

                                return next_line

            return None


        # ====================================================
        # ACCOUNT HOLDER
        # ====================================================

        holder = get_value_from_lines([
            "Customer",
            "Customer Name",
            "Account Holder",
            "Account Holder Name",
        ])

        if holder:

            details["account_holder"] = holder


        # ====================================================
        # ACCOUNT NUMBER
        # ====================================================

        account_number = get_value_from_lines([
            "Account Number",
            "Account No",
            "Account No.",
            "A/C Number",
            "A/C No",
            "A/C No.",
        ])

        if account_number:

            account_number = re.sub(
                r"[^A-Za-z0-9]",
                "",
                account_number,
            )

            details["account_number"] = (
                account_number
            )


        # ====================================================
        # IFSC
        # ====================================================

        ifsc_match = re.search(
            r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
            text.upper(),
        )

        if ifsc_match:

            details["ifsc"] = (
                ifsc_match.group(0)
            )


        # ====================================================
        # BANK NAME
        # ====================================================

        bank = get_value_from_lines([
            "Bank Name",
        ])

        if bank:

            invalid_bank_values = {
                "account statement",
                "statement",
                "account",
                "customer",
                "customer name",
                "name",
                "not detected",
            }

            if bank.strip().lower() not in (
                invalid_bank_values
            ):

                details["bank_name"] = (
                    bank.strip()
                )


        # ====================================================
        # FALLBACK BANK DETECTION
        # ====================================================

        if details["bank_name"] == "Not detected":

            known_banks = [
                "HDFC Bank",
                "ICICI Bank",
                "State Bank of India",
                "Axis Bank",
                "Kotak Mahindra Bank",
                "IndusInd Bank",
                "Yes Bank",
                "IDFC FIRST Bank",
                "Federal Bank",
                "Bank of Baroda",
                "Punjab National Bank",
                "Canara Bank",
                "Union Bank of India",
                "Bank of India",
                "Indian Bank",
                "AU Small Finance Bank",
                "RBL Bank",
                "South Indian Bank",
                "IDBI Bank",
                "Bandhan Bank",
            ]

            text_lower = text.lower()

            for bank_name in known_banks:

                if bank_name.lower() in text_lower:

                    details["bank_name"] = (
                        bank_name
                    )

                    break


        # ====================================================
        # BRANCH
        # ====================================================

        branch = get_value_from_lines([
            "Branch",
            "Branch Name",
            "Branch / City",
        ])

        if branch:

            details["branch"] = (
                branch.strip()
            )


        # ====================================================
        # STATEMENT PERIOD
        # ====================================================

        period = get_value_from_lines([
            "Statement Period",
            "Period",
        ])

        if period:

            details["statement_period"] = (
                period.strip()
            )


        # ====================================================
        # FALLBACK STATEMENT PERIOD
        # ====================================================

        if (
            details["statement_period"]
            == "Not detected"
        ):

            period_match = re.search(
                r"(\d{2}/\d{2}/\d{4})"
                r"\s*(?:to|-)\s*"
                r"(\d{2}/\d{2}/\d{4})",
                text,
            )

            if period_match:

                details["statement_period"] = (
                    f"{period_match.group(1)} "
                    f"to "
                    f"{period_match.group(2)}"
                )


        return details

    except Exception as e:

        print(
            f"Account detail extraction error: {e}"
        )

        return details


# ============================================================
# FIND DATAFRAME
# ============================================================

def find_dataframe(obj):

    if isinstance(obj, pd.DataFrame):

        return obj


    if isinstance(obj, dict):

        preferred_keys = [
            "transactions",
            "transaction_df",
            "processed_df",
            "data",
            "df",
            "result",
        ]

        for key in preferred_keys:

            if key in obj:

                found = find_dataframe(
                    obj[key]
                )

                if found is not None:

                    return found


        for value in obj.values():

            found = find_dataframe(value)

            if found is not None:

                return found


    if isinstance(obj, (tuple, list)):

        for item in obj:

            found = find_dataframe(item)

            if found is not None:

                return found


    return None


# ============================================================
# CATEGORY COLUMN
# ============================================================

def get_category_column(df):

    possible_columns = [
        "category",
        "classification",
        "transaction_category",
        "predicted_category",
        "class",
    ]

    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if normalized in possible_columns:

            return column

    return None


# ============================================================
# SAFE DISPLAY VALUE
# ============================================================

def safe_value(value):

    if value is None:

        return "Not detected"

    try:

        if pd.isna(value):

            return "Not detected"

    except Exception:

        pass

    value = str(value).strip()

    if not value:

        return "Not detected"

    return value


# ============================================================
# HIDE INTERNAL COLUMNS
# ============================================================

def get_display_dataframe(df):
    """
    Create a copy of the processed DataFrame for display
    and export.

    Internal processing columns are NOT removed from the
    original DataFrame.

    Currently hidden:
        Classification Method
    """

    display_df = df.copy()

    columns_to_hide = [
        "Classification Method",
    ]

    display_df = display_df.drop(
        columns=columns_to_hide,
        errors="ignore",
    )

    return display_df


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ⚙️ Processing Workflow"
    )

    st.caption(
        "Bank statement processing pipeline"
    )


    workflow_steps = [
        ("📄", "Upload Bank Statement"),
        ("🔍", "Detect PDF Type"),
        ("📑", "Extract Financial Data"),
        ("🔎", "Extract Transactions"),
        ("✅", "Validate Transactions"),
        ("🏷️", "Classify Transactions"),
        ("📊", "Display Results"),
        ("📥", "Export CSV / Excel"),
    ]


    for index, (icon, text) in enumerate(
        workflow_steps
    ):

        st.markdown(
            f"""
            <div class="workflow-box">
                <span class="workflow-number">
                    {index + 1}.
                </span>
                &nbsp;
                <span class="workflow-text">
                    {icon} {text}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


        if index < len(workflow_steps) - 1:

            st.markdown(
                '<div class="workflow-arrow">↓</div>',
                unsafe_allow_html=True,
            )


    st.divider()


    st.markdown(
        "### 🤖 Classification"
    )

    st.caption(
        "Transactions are classified using "
        "heuristic rules and traditional "
        "machine-learning methods."
    )


    st.divider()


    st.markdown(
        "### 📄 Supported Input"
    )

    st.markdown(
        """
        - Text-based PDFs
        - Scanned / image PDFs
        - Multiple bank layouts
        - Transaction extraction
        - Transaction classification
        - CSV export
        - Excel export
        """
    )


    st.divider()


    st.markdown(
        "### 🧹 Application"
    )


    if st.button(
        "🗑️ Clear Content",
        use_container_width=True,
    ):

        clear_application()

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="app-title">
        🏦 Bank Statement Processing & Classification System
    </div>

    <div class="app-subtitle">
        Extract, validate, classify and analyze transactions
        from bank statement PDFs.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📄 Upload Bank Statement'
    '</div>',
    unsafe_allow_html=True,
)


st.info(
    "Upload a bank statement PDF. The system automatically "
    "detects whether it is text-based or image-based."
)


uploaded_file = st.file_uploader(
    "Choose a bank statement PDF",
    type=["pdf"],
    label_visibility="collapsed",
)


# ============================================================
# FILE INFORMATION + PROCESS
# ============================================================

if uploaded_file is not None:

    file_size_kb = (
        uploaded_file.size / 1024
    )


    st.success(
        f"File uploaded successfully: "
        f"**{uploaded_file.name}**"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "File",
            uploaded_file.name,
        )


    with col2:

        st.metric(
            "File Size",
            f"{file_size_kb:.1f} KB",
        )


    with col3:

        st.metric(
            "Format",
            "PDF",
        )


    st.divider()


    # ========================================================
    # PROCESS BUTTON
    # ========================================================

    if st.button(
        "🚀 Process Bank Statement",
        type="primary",
        use_container_width=True,
    ):

        temp_path = None


        try:

            # ------------------------------------------------
            # Save uploaded file
            # ------------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # ------------------------------------------------
            # Extract account details
            # ------------------------------------------------

            account_details = (
                extract_account_details(
                    temp_path
                )
            )


            # ------------------------------------------------
            # Run processing pipeline
            # ------------------------------------------------

            with st.spinner(
                "Processing bank statement..."
            ):

                result = process_statement(
                    temp_path
                )


            # ------------------------------------------------
            # Find transaction DataFrame
            # ------------------------------------------------

            transactions_df = (
                find_dataframe(result)
            )


            if transactions_df is None:

                st.error(
                    "The processing pipeline did not "
                    "return transaction data."
                )

                st.write(
                    "Returned object type:",
                    type(result).__name__,
                )

                st.stop()


            transactions_df = (
                transactions_df.copy()
            )


            if transactions_df.empty:

                st.warning(
                    "No transactions were extracted "
                    "from this statement."
                )

                st.stop()


            # ------------------------------------------------
            # Save session state
            # ------------------------------------------------

            st.session_state.processed_df = (
                transactions_df
            )

            st.session_state.account_details = (
                account_details
            )

            st.session_state.uploaded_filename = (
                uploaded_file.name
            )

            st.session_state.processing_complete = (
                True
            )


            st.success(
                f"✅ Processing completed successfully. "
                f"{len(transactions_df)} transactions extracted."
            )


        except FileNotFoundError as e:

            st.error(
                f"❌ File error: {e}"
            )


        except ValueError as e:

            st.error(
                f"❌ Processing error: {e}"
            )


        except Exception as e:

            st.error(
                "❌ An unexpected error occurred "
                "while processing the statement."
            )

            st.exception(e)


        finally:

            # ------------------------------------------------
            # Delete temporary PDF
            # ------------------------------------------------

            if temp_path is not None:

                try:

                    if os.path.exists(temp_path):

                        os.remove(temp_path)

                except Exception:

                    pass


# ============================================================
# RESULTS
# ============================================================

if st.session_state.processed_df is not None:

    transactions_df = (
        st.session_state.processed_df
    )


    st.divider()


    st.markdown(
        '<div class="section-title">'
        '📊 Processing Results'
        '</div>',
        unsafe_allow_html=True,
    )


    if st.session_state.uploaded_filename:

        st.caption(
            f"Processed file: "
            f"**{st.session_state.uploaded_filename}**"
        )


    # ========================================================
    # ACCOUNT HOLDER DETAILS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '👤 Account Holder Details'
        '</div>',
        unsafe_allow_html=True,
    )


    details = (
        st.session_state.account_details
    )


    # ========================================================
    # ACCOUNT DETAILS ROW 1
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            "#### 👤 Account Holder"
        )

        st.info(
            safe_value(
                details.get(
                    "account_holder",
                    "Not detected",
                )
            )
        )


    with col2:

        st.markdown(
            "#### 🔢 Account Number"
        )

        st.info(
            safe_value(
                details.get(
                    "account_number",
                    "Not detected",
                )
            )
        )


    with col3:

        st.markdown(
            "#### 🏦 Bank Name"
        )

        st.info(
            safe_value(
                details.get(
                    "bank_name",
                    "Not detected",
                )
            )
        )


    # ========================================================
    # ACCOUNT DETAILS ROW 2
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            "#### 🏛️ IFSC Code"
        )

        st.info(
            safe_value(
                details.get(
                    "ifsc",
                    "Not detected",
                )
            )
        )


    with col2:

        st.markdown(
            "#### 📍 Branch"
        )

        st.info(
            safe_value(
                details.get(
                    "branch",
                    "Not detected",
                )
            )
        )


    with col3:

        st.markdown(
            "#### 📅 Statement Period"
        )

        st.info(
            safe_value(
                details.get(
                    "statement_period",
                    "Not detected",
                )
            )
        )


    # ========================================================
    # TRANSACTION SUMMARY
    # ========================================================

    st.divider()


    category_column = (
        get_category_column(
            transactions_df
        )
    )


    total_transactions = (
        len(transactions_df)
    )


    total_columns = (
        len(
            get_display_dataframe(
                transactions_df
            ).columns
        )
    )


    if category_column:

        total_categories = (
            transactions_df[
                category_column
            ]
            .fillna("Uncategorized")
            .astype(str)
            .nunique()
        )

    else:

        total_categories = 0


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Transactions",
            total_transactions,
        )


    with col2:

        st.metric(
            "Categories",
            total_categories,
        )


    with col3:

        st.metric(
            "Data Columns",
            total_columns,
        )


    # ========================================================
    # TRANSACTION TABLE
    # ========================================================

    st.divider()


    st.markdown(
        '<div class="section-title">'
        '💳 Transaction Data'
        '</div>',
        unsafe_allow_html=True,
    )


    st.caption(
        "Extracted and classified transaction data."
    )


    # --------------------------------------------------------
    # HIDE INTERNAL CLASSIFICATION METHOD COLUMN
    # --------------------------------------------------------

    display_df = get_display_dataframe(
        transactions_df
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500,
    )


    # ========================================================
    # CATEGORY ANALYSIS
    # ========================================================

    if category_column:

        st.divider()


        st.markdown(
            '<div class="section-title">'
            '📈 Category Analysis'
            '</div>',
            unsafe_allow_html=True,
        )


        category_counts = (
            transactions_df[
                category_column
            ]
            .fillna("Uncategorized")
            .astype(str)
            .value_counts()
        )


        chart_df = (
            category_counts
            .reset_index()
        )


        chart_df.columns = [
            "Category",
            "Count",
        ]


        total_category_transactions = (
            chart_df["Count"].sum()
        )


        chart_df["Percentage"] = (
            chart_df["Count"]
            / total_category_transactions
            * 100
        )


        chart_col, table_col = (
            st.columns([1.3, 1])
        )


        # ----------------------------------------------------
        # PIE CHART
        # ----------------------------------------------------

        with chart_col:

            st.markdown(
                "#### 🥧 Transaction Category Distribution"
            )


            st.vega_lite_chart(
                chart_df,
                {
                    "mark": {
                        "type": "arc",
                        "innerRadius": 70,
                        "tooltip": True,
                    },

                    "encoding": {

                        "theta": {
                            "field": "Count",
                            "type": "quantitative",
                        },

                        "color": {
                            "field": "Category",
                            "type": "nominal",
                            "legend": {
                                "title": "Category",
                            },
                        },

                        "tooltip": [

                            {
                                "field": "Category",
                                "type": "nominal",
                                "title": "Category",
                            },

                            {
                                "field": "Count",
                                "type": "quantitative",
                                "title": "Transactions",
                            },

                            {
                                "field": "Percentage",
                                "type": "quantitative",
                                "format": ".1f",
                                "title": "Percentage",
                            },
                        ],
                    },

                    "height": 400,
                },

                use_container_width=True,
            )


        # ----------------------------------------------------
        # CATEGORY PERCENTAGES
        # ----------------------------------------------------

        with table_col:

            st.markdown(
                "#### 📊 Category Percentages"
            )


            percentage_display = (
                chart_df.copy()
            )


            percentage_display[
                "Percentage"
            ] = (
                percentage_display[
                    "Percentage"
                ]
                .map(
                    lambda x:
                    f"{x:.1f}%"
                )
            )


            percentage_display.columns = [
                "Category",
                "Transactions",
                "Percentage",
            ]


            st.dataframe(
                percentage_display,
                use_container_width=True,
                hide_index=True,
            )


            st.caption(
                f"Total classified transactions: "
                f"{total_category_transactions}"
            )


    else:

        st.info(
            "No category/classification column "
            "was found in the processed data."
        )


    # ========================================================
    # EXPORT
    # ========================================================

    st.divider()


    st.markdown(
        '<div class="section-title">'
        '📥 Export Results'
        '</div>',
        unsafe_allow_html=True,
    )


    export_col1, export_col2 = (
        st.columns(2)
    )


    # ========================================================
    # CREATE CLEAN EXPORT DATAFRAME
    # ========================================================

    export_df = get_display_dataframe(
        transactions_df
    )


    # ========================================================
    # CSV EXPORT
    # ========================================================

    csv_data = (
        export_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    with export_col1:

        csv_clicked = st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="processed_bank_statement.csv",
            mime="text/csv",
            use_container_width=True,
        )


        if csv_clicked:

            st.toast(
                "File downloaded successfully! 📥",
                icon="✅",
            )


    # ========================================================
    # EXCEL EXPORT
    # ========================================================

    with export_col2:

        try:

            excel_buffer = BytesIO()


            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl",
            ) as writer:

                # --------------------------------------------
                # Transactions
                # --------------------------------------------

                export_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Transactions",
                )


                # --------------------------------------------
                # Category Summary
                # --------------------------------------------

                if category_column:

                    chart_df[
                        [
                            "Category",
                            "Count",
                            "Percentage",
                        ]
                    ].to_excel(
                        writer,
                        index=False,
                        sheet_name="Category Summary",
                    )


                # --------------------------------------------
                # Account Details
                # --------------------------------------------

                account_df = pd.DataFrame(
                    [
                        {
                            "Field": "Account Holder",
                            "Value": details.get(
                                "account_holder",
                                "Not detected",
                            ),
                        },
                        {
                            "Field": "Account Number",
                            "Value": details.get(
                                "account_number",
                                "Not detected",
                            ),
                        },
                        {
                            "Field": "Bank Name",
                            "Value": details.get(
                                "bank_name",
                                "Not detected",
                            ),
                        },
                        {
                            "Field": "IFSC Code",
                            "Value": details.get(
                                "ifsc",
                                "Not detected",
                            ),
                        },
                        {
                            "Field": "Branch",
                            "Value": details.get(
                                "branch",
                                "Not detected",
                            ),
                        },
                        {
                            "Field": "Statement Period",
                            "Value": details.get(
                                "statement_period",
                                "Not detected",
                            ),
                        },
                    ]
                )


                account_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Account Details",
                )


            excel_buffer.seek(0)


            excel_clicked = (
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_buffer,
                    file_name="processed_bank_statement.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )
            )


            if excel_clicked:

                st.toast(
                    "File downloaded successfully! 📥",
                    icon="✅",
                )


        except Exception as e:

            st.error(
                f"Excel export failed: {e}"
            )


# ============================================================
# TESTING TOOLS
# ============================================================

st.divider()

with st.expander(
    "🧪 Testing Tools — Generate Dummy Bank Statement",
    expanded=True,
):

    st.caption(
        "Generate a synthetic statement for testing. "
        "The generated PDF can then be downloaded and uploaded "
        "to the processor above."
    )

    if st.button(
        "🧪 Generate Dummy Statement",
        use_container_width=True,
    ):

        try:

            # ------------------------------------------------
            # Generate dummy PDF
            # ------------------------------------------------

            generated_file = (
                create_random_statement()
            )

            # ------------------------------------------------
            # Verify generated file
            # ------------------------------------------------

            if not os.path.exists(generated_file):

                st.error(
                    "The dummy statement was generated, "
                    "but the PDF file could not be found."
                )

            else:

                # --------------------------------------------
                # Read PDF into memory
                # --------------------------------------------

                with open(
                    generated_file,
                    "rb",
                ) as pdf_file:

                    pdf_data = pdf_file.read()

                # --------------------------------------------
                # Success message
                # --------------------------------------------

                st.success(
                    "Dummy statement generated successfully! 🎉"
                )

                # --------------------------------------------
                # Download button
                # --------------------------------------------

                st.download_button(
                    label="⬇️ Download Dummy Statement PDF",
                    data=pdf_data,
                    file_name="dummy_bank_statement.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

                # --------------------------------------------
                # Upload instruction
                # --------------------------------------------

                st.info(
                    "Download the PDF above and upload it "
                    "using the Bank Statement uploader."
                )

        except Exception as e:

            st.error(
                f"Failed to generate dummy statement: {e}"
            )