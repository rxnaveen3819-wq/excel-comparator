import streamlit as st
import pandas as pd

st.title("📊 Excel Stock Comparator")

# File uploader
file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

# Refresh button
if st.button("🔄 Refresh"):
    st.experimental_rerun()

if file1 and file2:
    # Read excel files
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Clean column names (remove spaces, lowercase for matching)
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()

    # Rename to standard names
    rename_map = {
        "stock name": "stock_name",
        "symbol": "symbol",
        "price": "price",
        "% chg": "chg"
    }
    df1 = df1.rename(columns=rename_map)
    df2 = df2.rename(columns=rename_map)

    # Merge on Stock Name + Symbol
    merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

    # Calculate Differences
    merged["price_diff"] = merged["price_1"] - merged["price_2"]
    merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]

    # Order by Chg_Diff desc
    merged = merged.sort_values(by="chg_diff", ascending=False)

    # Show table
    st.subheader("📑 Comparison Result")
    st.dataframe(
        merge
