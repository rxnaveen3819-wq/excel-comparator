import streamlit as st
import pandas as pd

st.title("📊 Excel Comparator - Stock Analysis")

# File upload
file1 = st.file_uploader("📂 Upload first Excel file", type=["xlsx"])
file2 = st.file_uploader("📂 Upload second Excel file", type=["xlsx"])

if file1 and file2:
    # Skip the title row
    df1 = pd.read_excel(file1, skiprows=1)
    df2 = pd.read_excel(file2, skiprows=1)

    st.subheader("✅ Columns Detected")
    st.write("📄 File 1 columns:", list(df1.columns))
    st.write("📄 File 2 columns:", list(df2.columns))

    # Correct column names based on your files
    required_cols = ["Stock Name", "Symbol", "Price", "% Chg"]

    if all(col in df1.columns for col in required_cols) and all(col in df2.columns for col in required_cols):
        # Merge on Stock Name + Symbol
        merged = pd.merge(df1, df2, on=["Stock Name", "Symbol"], suffixes=("_1", "_2"))

        # Calculate change difference
        merged["Chg_Diff"] = merged["% Chg_1"] - merged["% Chg_2"]

        # Sort by difference
        merged = merged.sort_values(by="Chg_Diff", ascending=False)

        # Show final result
        st.subheader("📊 Comparison Result")
        st.dataframe(
            merged[["Stock Name", "Symbol", "Price_1", "Price_2", "% Chg_1", "% Chg_2", "Chg_Diff"]],
            use_container_width=True
        )
    else:
        st.error("❌ Missing required columns. Please check above column names in your Excel files.")
