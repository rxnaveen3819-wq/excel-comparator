import streamlit as st
import pandas as pd

st.title("📊 Excel Comparator - Stock Analysis")

# File upload
file1 = st.file_uploader("📂 Upload first Excel file", type=["xlsx"])
file2 = st.file_uploader("📂 Upload second Excel file", type=["xlsx"])

if file1 and file2:
    # Try skipping the first row (title row)
    df1 = pd.read_excel(file1, skiprows=1)
    df2 = pd.read_excel(file2, skiprows=1)

    st.subheader("✅ Columns Detected")
    st.write("📄 File 1 columns:", list(df1.columns))
    st.write("📄 File 2 columns:", list(df2.columns))

    # Check if required columns exist
    required_cols = ["stock_name", "symbol", "price", "chg"]
    if all(col in df1.columns for col in required_cols) and all(col in df2.columns for col in required_cols):
        # Merge on stock name + symbol
        merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

        # Calculate change difference
        merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]

        # Sort by difference (descending)
        merged = merged.sort_values(by="chg_diff", ascending=False)

        # Show final table
        st.subheader("📊 Comparison Result")
        st.dataframe(
            merged[["stock_name", "symbol", "price_1", "price_2", "chg_1", "chg_2", "chg_diff"]],
            use_container_width=True
        )
    else:
        st.error("❌ Missing required columns. Please check above column names. Maybe increase skiprows.")
