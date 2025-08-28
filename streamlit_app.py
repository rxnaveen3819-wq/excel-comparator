import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

st.title("📊 Stock Comparison Tool")

# Upload files
file1 = st.file_uploader("Upload File 1", type=["xlsx"])
file2 = st.file_uploader("Upload File 2", type=["xlsx"])

def generate_pdf(dataframe: pd.DataFrame) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Stock Comparison Report", styles['Title']))

    table_data = [list(dataframe.columns)] + dataframe.astype(str).values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

if file1 and file2:
    try:
        # Read: skip title row
        df1 = pd.read_excel(file1, skiprows=1)
        df2 = pd.read_excel(file2, skiprows=1)

        required_cols = ["Stock Name", "Symbol", "% Chg", "Price"]
        if not all(col in df1.columns for col in required_cols) or not all(col in df2.columns for col in required_cols):
            st.error("❌ Missing required columns. Make sure both files have: Stock Name, Symbol, % Chg, Price.")
        else:
            # Merge on Stock Name + Symbol
            merged = pd.merge(df1, df2, on=["Stock Name", "Symbol"], suffixes=("_1", "_2"))

            # Ensure numeric for calculations/sorting
            for col in ["% Chg_1", "% Chg_2", "Price_1", "Price_2"]:
                if col in merged.columns:
                    merged[col] = pd.to_numeric(merged[col], errors="coerce")

            # Differences
            merged["chg_diff"] = merged["% Chg_2"] - merged["% Chg_1"]
            merged["price_diff"] = merged["Price_2"] - merged["Price_1"]

            # Arrange columns
            result = merged[
                ["Stock Name", "Symbol",
                 "% Chg_1", "% Chg_2", "chg_diff",
                 "Price_1", "Price_2", "price_diff"]
            ]

            # 👉 Sort by chg_diff DESC
            result = result.sort_values(by="chg_diff", ascending=False)

            st.success("✅ Comparison completed (ordered by chg_diff desc)!")
            st.dataframe(result, use_container_width=True)

            # Download as PDF
            pdf_buffer = generate_pdf(result)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name="stock_comparison.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

