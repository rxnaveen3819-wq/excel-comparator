import streamlit as st
import pandas as pd
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

st.title("📊 Excel Comparator App")

# Upload two Excel files
file1 = st.file_uploader("Upload First Excel File", type=["xlsx"])
file2 = st.file_uploader("Upload Second Excel File", type=["xlsx"])

# PDF Export Function
def export_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    style = getSampleStyleSheet()
    elements.append(Paragraph("📊 Stock Comparison Report", style['Title']))

    # Convert dataframe to list of lists
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

if file1 and file2:
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        # Normalize column names (lowercase & no spaces)
        df1.columns = df1.columns.str.strip().str.lower()
        df2.columns = df2.columns.str.strip().str.lower()

        # Ensure required columns exist
        required_cols = ["stock name", "symbol", "price", "chg"]
        for col in required_cols:
            if col not in df1.columns or col not in df2.columns:
                st.error(f"❌ Missing column: {col}")
                st.stop()

        # Merge on stock name and symbol
        merged = pd.merge(df1, df2, on=["stock name", "symbol"], suffixes=("_1", "_2"))

        # Calculate differences
        merged["price_diff"] = merged["price_1"] - merged["price_2"]
        merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]

        # Show results
        st.subheader("Comparison Results")
        st.dataframe(merged)

        # Download as Excel
        excel_buffer = io.BytesIO()
        merged.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        st.download_button(
            label="📥 Download as Excel",
            data=excel_buffer,
            file_name="comparison_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Download as PDF
        pdf_file = export_pdf(merged)
        st.download_button(
            label="📥 Download as PDF",
            data=pdf_file,
            file_name="comparison_report.pdf",
            mime="application/pdf"
        )

        # Refresh button
        if st.button("🔄 Refresh / Reset"):
            st.experimental_rerun()

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
