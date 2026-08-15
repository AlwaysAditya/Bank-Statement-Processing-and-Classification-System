import os
import tempfile
from pathlib import Path

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
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🏦 Bank Statement Processing & Classification System")

st.write(
    "Upload a bank statement PDF to extract, validate, "
    "and classify transactions using a non-LLM approach."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("System")

    st.success("✓ PDF Processing")
    st.success("✓ Text PDF Support")
    st.success("✓ Image PDF / OCR Support")
    st.success("✓ Transaction Extraction")
    st.success("✓ Validation")
    st.success("✓ Non-LLM Classification")
    st.success("✓ CSV Export")
    st.success("✓ Excel Export")


# ============================================================
# TESTING TOOLS
# ============================================================

st.subheader("🧪 Testing Tools")

st.caption(
    "Generate a synthetic bank statement for testing "
    "the complete processing pipeline."
)

if st.button(
    "🧪 Generate Dummy Statement",
    use_container_width=True
):

    try:

        generated_file = create_random_statement()

        st.success(
            "Dummy statement generated successfully."
        )

        st.code(
            str(generated_file)
        )

        st.info(
            "You can now upload this PDF below."
        )

    except Exception as e:

        st.error(
            f"Failed to generate dummy statement: {e}"
        )


st.divider()


# ============================================================
# PDF UPLOAD
# ============================================================

st.subheader("📄 Upload Bank Statement")

uploaded_file = st.file_uploader(
    "Upload Bank Statement PDF",
    type=["pdf"],
    help="Upload either a text-based or scanned/image-based bank statement."
)


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file is not None:

    st.success(
        f"File uploaded: **{uploaded_file.name}**"
    )

    st.write(
        f"File size: **{uploaded_file.size / 1024:.2f} KB**"
    )

    process_button = st.button(
        "🚀 Process Bank Statement",
        type="primary",
        use_container_width=True
    )

    if process_button:

        temp_path = None

        try:

            # ====================================================
            # SAVE UPLOADED PDF TO TEMPORARY FILE
            # ====================================================

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # ====================================================
            # RUN COMPLETE PIPELINE
            # ====================================================

            with st.spinner(
                "Processing bank statement..."
            ):

                transactions_df = process_statement(
                    temp_path
                )


            # ====================================================
            # VALIDATE RESULT
            # ====================================================

            if transactions_df is None:

                st.error(
                    "The processing pipeline returned no result."
                )

                st.stop()


            if not isinstance(
                transactions_df,
                pd.DataFrame
            ):

                st.error(
                    "The processing pipeline did not return a DataFrame."
                )

                st.stop()


            if transactions_df.empty:

                st.warning(
                    "No transactions were extracted from the statement."
                )

                st.stop()


            # ====================================================
            # SUCCESS
            # ====================================================

            st.success(
                f"✅ Processing completed successfully — "
                f"{len(transactions_df)} transactions extracted."
            )


            # ====================================================
            # SUMMARY METRICS
            # ====================================================

            st.subheader("📊 Processing Summary")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Transactions",
                    len(transactions_df)
                )

            with col2:

                st.metric(
                    "Columns",
                    len(transactions_df.columns)
                )

            with col3:

                if "Category" in transactions_df.columns:

                    category_count = (
                        transactions_df["Category"]
                        .nunique()
                    )

                elif "category" in transactions_df.columns:

                    category_count = (
                        transactions_df["category"]
                        .nunique()
                    )

                else:

                    category_count = 0

                st.metric(
                    "Categories",
                    category_count
                )


            # ====================================================
            # TRANSACTION DATA
            # ====================================================

            st.subheader("💳 Processed Transactions")

            st.dataframe(
                transactions_df,
                use_container_width=True,
                hide_index=True
            )


            # ====================================================
            # CATEGORY SUMMARY
            # ====================================================

            category_column = None

            for column in transactions_df.columns:

                if column.lower() in [
                    "category",
                    "classification",
                    "transaction_category"
                ]:

                    category_column = column
                    break


            if category_column is not None:

                st.subheader("📈 Transaction Categories")

                category_summary = (
                    transactions_df[
                        category_column
                    ]
                    .value_counts()
                    .reset_index()
                )

                category_summary.columns = [
                    "Category",
                    "Transaction Count"
                ]

                st.dataframe(
                    category_summary,
                    use_container_width=True,
                    hide_index=True
                )


            # ====================================================
            # EXPORT
            # ====================================================

            st.subheader("📥 Export Results")

            col1, col2 = st.columns(2)


            # ----------------------------------------------------
            # CSV
            # ----------------------------------------------------

            csv_data = transactions_df.to_csv(
                index=False
            ).encode("utf-8")


            with col1:

                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name="processed_bank_statement.csv",
                    mime="text/csv",
                    use_container_width=True
                )


            # ----------------------------------------------------
            # EXCEL
            # ----------------------------------------------------

            excel_buffer = None

            try:

                from io import BytesIO

                excel_buffer = BytesIO()

                with pd.ExcelWriter(
                    excel_buffer,
                    engine="openpyxl"
                ) as writer:

                    transactions_df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Transactions"
                    )

                    if category_column is not None:

                        category_summary.to_excel(
                            writer,
                            index=False,
                            sheet_name="Category Summary"
                        )

                excel_buffer.seek(0)


                with col2:

                    st.download_button(
                        label="⬇️ Download Excel",
                        data=excel_buffer,
                        file_name="processed_bank_statement.xlsx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                        use_container_width=True
                    )


            except Exception as e:

                with col2:

                    st.error(
                        f"Excel export failed: {e}"
                    )


        # ========================================================
        # ERROR HANDLING
        # ========================================================

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
                "❌ An unexpected error occurred while "
                "processing the statement."
            )

            st.exception(e)


        # ========================================================
        # CLEANUP TEMPORARY FILE
        # ========================================================

        finally:

            if temp_path is not None:

                try:

                    if os.path.exists(temp_path):

                        os.remove(temp_path)

                except Exception:

                    pass