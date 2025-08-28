import streamlit as st
import pandas as pd

st.title("📊 Excel Stock Comparator")

# Refresh button → clears uploaded files
if st.button("🔄 Refresh"):
    st.session_state.clear()
    st.rerun()

# File upload
file1 = st.file_uploader("Upload First Excel File", type=["xlsx"], key="file1")
file2 = st.file_uploader("Upload Second Excel File", type=["xlsx"], key="file2")

if file1 and file2:
    # Load files (skip first row to use proper headers)
    df1 = pd.read_excel(file1, skiprows=1)
    df2 = pd.read_excel(file2, skiprows=1)

    # Rename columns consistently
    rename_map = {
        "Stock Name": "stock_name",
        "Symbol": "symbol",
        "% Chg": "chg",
        "Price": "price",
        "Volume": "volume"
    }
    df1 = df1.rename(columns=rename_map)
    df2 = df2.rename(columns=rename_map)

    # Merge on stock name + symbol
    merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

    # Calculate differences
    merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]
    merged["price_diff"] = merged["price_1"] - merged["price_2"]
    merged["volume_diff"] = merged["volume_1"] - merged["volume_2"]

    # Sort by %chg difference
    merged = merged.sort_values(by="chg_diff", ascending=False)

    st.subheader("📈 Comparison Result")
    st.dataframe(
        merged[
            ["stock_name", "symbol", "chg_1", "chg_2", "chg_diff",
             "price_1", "price_2", "pr
