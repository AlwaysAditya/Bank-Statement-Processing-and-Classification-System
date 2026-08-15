import os
import tempfile
from io import BytesIO

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
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN PAGE
       ======================================================== */

    .main {
        padding-top: 1rem;
    }

    .app-title {
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .app-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }


    /* ========================================================
       SECTION HEADINGS
       ======================================================== */

    .section-title {
        font-size: 1.35rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .workflow-step {
        padding: 0.55rem 0.7rem;
        margin-bottom: 0.2rem;
        border-radius: 0.5rem;
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
    }

    .workflow-arrow {
        text-align: center;
        font-size: 1rem;
        color: #6b7280;
        margin: 0.1rem 0;
    }


    /* ========================================================
       INFO CARDS
       ======================================================== */

    .info-card {
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "account_details" not in st.session_state:

    st.session_state.account_details = None

if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "generated_file" not in st.session_state:
    st.session_state.generated_file = None


# ============================================================
# CALLBACKS
# ============================================================

def clear_content():

    generated_file = (
        st.session_state.get(
            "generated_file"
        )
    )

    if generated_file:

        try:

            if os.path.exists(
                generated_file
            ):

                os.remove(
                    generated_file
                )

        except Exception:

            pass


    st.session_state.processed_df = None

    st.session_state.account_details = None

    st.session_state.uploaded_filename = None

    st.session_state.generated_file = None

    st.session_state.uploader_key += 1


def csv_download_notice():
    """
    Show confirmation after CSV download button is clicked.
    """

    st.toast(
        "✅ CSV file is downloaded!",
        icon="📥"
    )


def excel_download_notice():
    """
    Show confirmation after Excel download button is clicked.
    """

    st.toast(
        "✅ Excel file is downloaded!",
        icon="📥"
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Processing Workflow")

    st.caption(
        "Bank statement processing pipeline"
    )

    # ========================================================
    # WORKFLOW
    # ========================================================

    workflow_steps = [

        "📄 Upload Bank Statement",

        "🔍 Detect PDF Type",

        "📑 Extract Financial Data",

        "🔎 Extract Transactions",

        "✅ Validate Transactions",

        "🏷️ Rule-Based Classification",

        "🤖 ML Classification Fallback",

        "📊 Display Results",

        "📥 Export CSV / Excel",
    ]


    for i, step in enumerate(workflow_steps):

        st.markdown(
            f"""
            <div class="workflow-step">
                <strong>{i + 1}.</strong> {step}
            </div>
            """,
            unsafe_allow_html=True
        )

        if i < len(workflow_steps) - 1:

            st.markdown(
                '<div class="workflow-arrow">↓</div>',
                unsafe_allow_html=True
            )


    st.divider()


    # ========================================================
    # CLASSIFICATION
    # ========================================================

    st.markdown("### 🤖 Classification Engine")

    st.markdown(
        """
        **1. Rule-Based**

        Existing heuristic keyword matching.

        **2. Traditional ML**

        TF-IDF + Logistic Regression.

        **3. Hybrid**

        Rules are checked first.  
        ML handles transactions that
        rules cannot confidently classify.
        """
    )


    st.divider()


    # ========================================================
    # SUPPORTED INPUT
    # ========================================================

    st.markdown("### 📄 Supported Input")

    st.markdown(
        """
        - Text-based PDFs
        - Scanned / image PDFs
        - Multiple bank layouts
        - Transaction extraction
        - Non-LLM classification
        - CSV export
        - Excel export
        """
    )


    st.divider()


    # ========================================================
    # CLEAR CONTENT
    # ========================================================

    st.markdown("### 🧹 Session Controls")

    st.caption(
        "Clear the currently uploaded and processed content."
    )

    st.button(
        "🗑️ Clear Content",
        use_container_width=True,
        on_click=clear_content
    )


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
        from bank statement PDFs using non-LLM approaches.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📄 Upload Bank Statement</div>',
    unsafe_allow_html=True
)

st.info(
    "Upload a bank statement PDF. The system automatically "
    "detects whether it is text-based or image-based and "
    "selects the appropriate processing pipeline."
)


uploaded_file = st.file_uploader(
    "Choose a bank statement PDF",
    type=["pdf"],
    label_visibility="collapsed",
    help="Only PDF files are supported.",
    key=f"bank_statement_uploader_{st.session_state.uploader_key}"
)


# ============================================================
# FILE INFORMATION
# ============================================================

if uploaded_file is not None:

    file_size_kb = uploaded_file.size / 1024

    st.success(
        f"File uploaded successfully: **{uploaded_file.name}**"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "File",
            uploaded_file.name
        )

    with col2:

        st.metric(
            "File Size",
            f"{file_size_kb:.1f} KB"
        )

    with col3:

        st.metric(
            "Format",
            "PDF"
        )


    st.divider()


    # ========================================================
    # PROCESS BUTTON
    # ========================================================

    if st.button(
        "🚀 Process Bank Statement",
        type="primary",
        use_container_width=True
    ):

        temp_path = None

        try:

            # ------------------------------------------------
            # Save uploaded PDF temporarily
            # ------------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # ------------------------------------------------
            # Run processing pipeline
            # ------------------------------------------------

            with st.spinner(
                "Processing bank statement..."
            ):

                transactions_df = process_statement(
                    temp_path
                )


            # ------------------------------------------------
            # Validate output
            # ------------------------------------------------

            if transactions_df is None:

                st.error(
                    "The processing pipeline returned no data."
                )

                st.stop()


            if not isinstance(
                transactions_df,
                pd.DataFrame
            ):

                st.error(
                    "The processing pipeline did not return "
                    "a pandas DataFrame."
                )

                st.stop()


            if transactions_df.empty:

                st.warning(
                    "No transactions were extracted "
                    "from this statement."
                )

                st.stop()


            # ------------------------------------------------
            # Store result
            # ------------------------------------------------

            st.session_state.processed_df = (
                transactions_df
            )

            st.session_state.uploaded_filename = (
                uploaded_file.name
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
# ACCOUNT INFORMATION
# ============================================================

if st.session_state.get("account_details"):

    account_details = (
        st.session_state.account_details
    )

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '👤 Account Information'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Account information extracted from the bank statement."
    )


    # --------------------------------------------------------
    # Account number masking
    # --------------------------------------------------------

    account_number = (
        account_details.get(
            "account_number"
        )
    )


    if account_number:

        account_number = str(
            account_number
        )

        if len(account_number) > 4:

            masked_account_number = (
                "X" * (
                    len(account_number) - 4
                )
                + account_number[-4:]
            )

        else:

            masked_account_number = (
                account_number
            )

    else:

        masked_account_number = "Not detected"


    # --------------------------------------------------------
    # Values
    # --------------------------------------------------------

    bank_name = (
        account_details.get(
            "bank_name"
        )
        or "Not detected"
    )

    account_holder = (
        account_details.get(
            "account_holder_name"
        )
        or "Not detected"
    )

    ifsc = (
        account_details.get(
            "ifsc"
        )
        or "Not detected"
    )

    branch = (
        account_details.get(
            "branch"
        )
        or "Not detected"
    )

    statement_period = (
        account_details.get(
            "statement_period"
        )
        or "Not detected"
    )


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Account Holder",
            account_holder
        )

    with col2:

        st.metric(
            "Account Number",
            masked_account_number
        )

    with col3:

        st.metric(
            "Bank",
            bank_name
        )


    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "IFSC",
            ifsc
        )

    with col5:

        st.metric(
            "Branch",
            branch
        )

    with col6:

        st.metric(
            "Statement Period",
            statement_period
        )

# ============================================================
# RESULTS
# ============================================================

if st.session_state.processed_df is not None:

    transactions_df = (
        st.session_state.processed_df
    )


    st.divider()


    # ========================================================
    # RESULTS HEADER
    # ========================================================

    st.markdown(
        '<div class="section-title">📊 Processing Results</div>',
        unsafe_allow_html=True
    )


    if st.session_state.uploaded_filename:

        st.caption(
            f"Processed file: "
            f"**{st.session_state.uploaded_filename}**"
        )


    # ========================================================
    # FIND CATEGORY COLUMN
    # ========================================================

    category_column = None

    for column in transactions_df.columns:

        normalized_column = (
            str(column)
            .strip()
            .lower()
        )

        if normalized_column in [
            "category",
            "classification",
            "transaction_category"
        ]:

            category_column = column

            break


    # ========================================================
    # FIND CLASSIFICATION METHOD
    # ========================================================

    method_column = None

    for column in transactions_df.columns:

        normalized_column = (
            str(column)
            .strip()
            .lower()
        )

        if normalized_column == (
            "classification method"
        ):

            method_column = column

            break


    # ========================================================
    # FIND CONFIDENCE COLUMN
    # ========================================================

    confidence_column = None

    for column in transactions_df.columns:

        normalized_column = (
            str(column)
            .strip()
            .lower()
        )

        if normalized_column in [
            "classification confidence",
            "confidence"
        ]:

            confidence_column = column

            break


    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    total_transactions = len(
        transactions_df
    )

    total_columns = len(
        transactions_df.columns
    )


    if category_column is not None:

        total_categories = (
            transactions_df[
                category_column
            ]
            .fillna("Uncategorized")
            .nunique()
        )

    else:

        total_categories = 0


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Transactions",
            total_transactions
        )


    with col2:

        st.metric(
            "Categories",
            total_categories
        )


    with col3:

        st.metric(
            "Data Columns",
            total_columns
        )


    # ========================================================
    # CLASSIFICATION SUMMARY
    # ========================================================

    if method_column is not None:

        st.divider()

        st.markdown(
            "### 🤖 Classification Summary"
        )

        method_counts = (
            transactions_df[
                method_column
            ]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )


        summary_col1, summary_col2 = (
            st.columns(2)
        )


        with summary_col1:

            rule_count = method_counts.get(
                "Rule-Based",
                0
            )

            st.metric(
                "Rule-Based",
                int(rule_count)
            )


        with summary_col2:

            ml_count = method_counts.get(
                "TF-IDF + Logistic Regression",
                0
            )

            st.metric(
                "ML Classified",
                int(ml_count)
            )


    st.divider()


    # ========================================================
    # TRANSACTION DATA
    # ========================================================

    st.markdown(
        '<div class="section-title">💳 Transaction Data</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Extracted and classified transaction data "
        "from the processing pipeline."
    )


    st.dataframe(
        transactions_df,
        use_container_width=True,
        hide_index=True,
        height=500
    )


    # ========================================================
    # CATEGORY ANALYSIS
    # ========================================================

    if category_column is not None:

        st.divider()

        st.markdown(
            '<div class="section-title">'
            '📈 Category Analysis'
            '</div>',
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # Category counts
        # ----------------------------------------------------

        category_counts = (
            transactions_df[
                category_column
            ]
            .fillna("Uncategorized")
            .astype(str)
            .value_counts()
        )


        total_category_transactions = (
            category_counts.sum()
        )


        # ----------------------------------------------------
        # Chart Data
        # ----------------------------------------------------

        chart_df = (
            category_counts
            .reset_index()
        )

        chart_df.columns = [
            "Category",
            "Count"
        ]


        chart_df["Percentage"] = (
            chart_df["Count"]
            / total_category_transactions
            * 100
        )


        # ----------------------------------------------------
        # Chart + Table
        # ----------------------------------------------------

        chart_col, table_col = (
            st.columns([1.3, 1])
        )


        # ====================================================
        # PIE CHART
        # ====================================================

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
                        "tooltip": True
                    },

                    "encoding": {

                        "theta": {
                            "field": "Count",
                            "type": "quantitative"
                        },

                        "color": {
                            "field": "Category",
                            "type": "nominal",
                            "legend": {
                                "title": "Category"
                            }
                        },

                        "tooltip": [

                            {
                                "field": "Category",
                                "type": "nominal",
                                "title": "Category"
                            },

                            {
                                "field": "Count",
                                "type": "quantitative",
                                "title": "Transactions"
                            },

                            {
                                "field": "Percentage",
                                "type": "quantitative",
                                "format": ".1f",
                                "title": "Percentage"
                            }
                        ]
                    },

                    "height": 400
                },

                use_container_width=True
            )


        # ====================================================
        # CATEGORY PERCENTAGES
        # ====================================================

        with table_col:

            st.markdown(
                "#### 📊 Category Percentages"
            )


            percentage_display = (
                chart_df[
                    [
                        "Category",
                        "Count",
                        "Percentage"
                    ]
                ]
                .copy()
            )


            percentage_display["Percentage"] = (
                percentage_display["Percentage"]
                .map(
                    lambda x: f"{x:.1f}%"
                )
            )


            percentage_display.columns = [
                "Category",
                "Transactions",
                "Percentage"
            ]


            st.dataframe(
                percentage_display,
                use_container_width=True,
                hide_index=True
            )


            st.caption(
                f"Total classified transactions: "
                f"{total_category_transactions}"
            )


    else:

        st.info(
            "No category/classification column was found "
            "in the processed data."
        )


    # ========================================================
    # EXPORT
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">📥 Export Results</div>',
        unsafe_allow_html=True
    )


    export_col1, export_col2 = (
        st.columns(2)
    )


    # ========================================================
    # CSV
    # ========================================================

    csv_data = (
        transactions_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    with export_col1:

        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="processed_bank_statement.csv",
            mime="text/csv",
            use_container_width=True,
            on_click=csv_download_notice
        )


    # ========================================================
    # EXCEL
    # ========================================================

    with export_col2:

        try:

            excel_buffer = BytesIO()


            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                # --------------------------------------------
                # Transactions
                # --------------------------------------------

                transactions_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Transactions"
                )


                # --------------------------------------------
                # Category Summary
                # --------------------------------------------

                if category_column is not None:

                    chart_df[
                        [
                            "Category",
                            "Count",
                            "Percentage"
                        ]
                    ].to_excel(
                        writer,
                        index=False,
                        sheet_name="Category Summary"
                    )


                # --------------------------------------------
                # Classification Summary
                # --------------------------------------------

                if method_column is not None:

                    method_counts.reset_index().rename(
                        columns={
                            method_column: "Method",
                            "count": "Transactions"
                        }
                    ).to_excel(
                        writer,
                        index=False,
                        sheet_name="Classification Summary"
                    )


            excel_buffer.seek(0)


            st.download_button(
                label="⬇️ Download Excel",
                data=excel_buffer,
                file_name="processed_bank_statement.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
                on_click=excel_download_notice
            )


        except Exception as e:

            st.error(
                f"Excel export failed: {e}"
            )


# ============================================================
# TESTING TOOLS
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🧪 Testing Tools</div>',
    unsafe_allow_html=True
)

st.caption(
    "Generate a synthetic bank statement for testing "
    "the PDF extraction and classification pipeline."
)


testing_col1, testing_col2 = st.columns(
    [1, 2]
)


with testing_col1:

    if st.button(
        "🧪 Generate Dummy Statement",
        use_container_width=True
    ):

        try:

            generated_file = (
                create_random_statement()
            )


            st.session_state.generated_file = (
                str(generated_file)
            )


            st.success(
                "Dummy statement generated successfully."
            )


        except Exception as e:

            st.error(
                f"Failed to generate dummy statement: {e}"
            )


with testing_col2:

    generated_file = (
        st.session_state.get(
            "generated_file"
        )
    )


    if generated_file:

        st.caption(
            "Generated test file:"
        )

        st.code(
            str(generated_file)
        )

        st.info(
            "Upload the generated PDF using "
            "the uploader above to test the pipeline."
        )