import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📊 Excel Comparator App")

# Upload two Excel files
file1 = st.file_uploader("Upload first Excel file", type=["xlsx", "xls"])
file2 = st.file_uploader("Upload second Excel file", type=["xlsx", "xls"])

def read_excel_normalize(f):
    df = pd.read_excel(f)
    # normalize headers: trim + lowercase (so "Stock Name" -> "stock name", "%Chg" -> "%chg")
    df.columns = df.columns.str.strip().str.lower()
    return df

if file1 and file2:
    df1 = read_excel_normalize(file1)
    df2 = read_excel_normalize(file2)

    # Ensure required columns exist
    required = {"stock name", "%chg", "price"}
    missing1 = sorted(list(required - set(df1.columns)))
    missing2 = sorted(list(required - set(df2.columns)))
    if missing1 or missing2:
        st.error(f"Missing columns -> Excel 1: {missing1 or 'OK'},  Excel 2: {missing2 or 'OK'}")
    else:
        # Merge on Stock Name
        merged = pd.merge(df1, df2, on="stock name", suffixes=("_1", "_2"), how="inner")

        # Clean %chg columns (drop % sign, handle strings/numbers) and cast to float
        for col in ["%chg_1", "%chg_2"]:
            merged[col] = (
                merged[col]
                .astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", "", regex=False)
            )
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

        # Prices -> numeric
        for col in ["price_1", "price_2"]:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

        # Differences
        merged["%chg_diff"] = merged["%chg_1"] - merged["%chg_2"]
        merged["price_diff"] = merged["price_1"] - merged["price_2"]

        # Sort by %Chg_1 (desc)
        merged = merged.sort_values(by="%chg_1", ascending=False)

        # Final view
        out = merged[[
            "stock name",
            "%chg_1", "%chg_2", "%chg_diff",
            "price_1", "price_2", "price_diff"
        ]]
        st.subheader("📑 Comparison Result (sorted by %Chg_1 desc)")
        st.dataframe(out)

        # ---- Download as Excel (use a BytesIO buffer) ----
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            out.to_excel(writer, index=False, sheet_name="Comparison")
        buffer.seek(0)

        st.download_button(
            label="📥 Download Result Excel",
            data=buffer,
            file_name="comparison_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
