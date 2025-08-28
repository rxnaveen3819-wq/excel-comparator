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

if file1 and file2:
    try:
        # Read Excel with skiprows to remove first line
        df1 = pd.read_excel(file1, skiprows=1)
        df2 = pd.read_excel(file2, skiprows=1)

        required_cols = ["Stock Name", "Symbol", "% Chg", "Price"]

        if not all(col in df1.columns for col in required_cols) or not all(col in df2.columns for col in required_cols):
            st.error("❌ Missing required columns. Please check your Excel file headers.")
        else:
            # Merge
            merged = pd.merge(df1, df2, on=["Stock Name", "Symbol"], suffixes=("_1", "_2"))

            # Differences
            merged["chg_diff"] = merged["% Chg_2"] - merged["% Chg_1"]
            merged["price_diff"] = merged["Price_2"] - merged["Price_1"]

            # Select columns
            result = merged[[
                "Stock Name", "Symbol",
                "% Chg_1", "% Chg_2", "chg_diff",
                "Price_1", "Price_2", "price_diff"
            ]]

            st.success("✅ Comparison completed!")
            st.dataframe(result)

            # --- PDF Export ---
            def generate_pdf(dataframe):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                elements.append(Paragraph("Stock Comparison Report", styles['Title']))

                # Convert DataFrame to list of lists
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

            pdf_buffer = generate_pdf(result)

            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name="stock_comparison.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
