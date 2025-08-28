import streamlit as st
import pandas as pd

st.title("📊 Excel Stock Comparator")

# File upload
file1 = st.file_uploader("Upload First Excel File", type=["xlsx"])
file2 = st.file_uploader("Upload Second Excel File", type=["xlsx"])

if file1 and file2:
    # Load files (skip first row to use proper headers)
    df1 = pd.read_excel(file1, skiprows=1)
    df2 = pd.read_excel(file2, skiprows=1)

    # Rename columns consistently
    df1 = df1.rename(columns={
        "Stock Name": "stock_name",
        "Symbol": "symbol",
        "% Chg": "chg",
        "Price": "price",
        "Volume": "volume"
    })
    df2 = df2.rename(columns={
        "Stock Name": "stock_name",
        "Symbol": "symbol",
        "% Chg": "chg",
        "Price": "price",
        "Volume": "volume"
    })

    # Merge on stock name + symbol
    merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

    # Calculate difference in %chg
    merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]

    # Sort by difference
    merged = merged.sort_values(by="chg_diff", ascending=False)

    st.subheader("📈 Comparison Result")
    st.dataframe(merged[["stock_name", "symbol", "chg_1", "chg_2", "chg_diff"]])

    # Refresh button
    if st.button("🔄 Refresh"):
        st.experimental_rerun()
