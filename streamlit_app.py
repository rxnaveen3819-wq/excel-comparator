import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

st.title("📊 Excel Comparator with PDF Export")

# Upload files
file1 = st.file_uploader("Upload first Excel file", type=["xlsx"])
file2 = st.file_uploader("Upload second Excel file", type=["xlsx"])

if file1 and file2:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # 🔍 Debug step: Show actual column names
    st.write("✅ File 1 columns:", list(df1.columns))
    st.write("✅ File 2 columns:", list(df2.columns))

    # --- IMPORTANT ---
    # Once you see the real column names above, we will rename them here.
    # Example (you must adjust according to what you see):
    # df1.rename(columns={"Stock Name": "stock_name", "Symbol": "symbol"}, inplace=True)
    # df2.rename(columns={"Stock Name": "stock_name", "Symbol": "symbol"}, inplace=True)

    # Merge only if required columns exist
    if "stock_name" in df1.columns and "symbol" in df1.columns and \
       "stock_name" in df2.columns and "symbol" in df2.columns:

        merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

        # Example: compare price and change
        if "price_1" in merged.columns and "price_2" in merged.columns:
            merged["price_diff"] = merged["price_1"] - merged["price_2"]
        if "chg_1" in merged.columns and "chg_2" in merged.columns:
            merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]

        st.dataframe(merged)

        # Download as PDF
        def create_pdf(dataframe):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            style = getSampleStyleSheet()

            data = [list(dataframe.columns)] + dataframe.values.tolist()
            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(Paragraph("Excel Comparison Report", style["Title"]))
            elements.append(table)
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf(merged)
        st.download_button("⬇️ Download PDF", data=pdf_buffer,
                           file_name="comparison_report.pdf",
                           mime="application/pdf")

    else:
        st.error("❌ Missing columns. Please check above 'File 1 columns' and 'File 2 columns'.")
