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

    # Merge on Stock Name + Symbol
    merged = pd.merge(df1, df2, on=["Stock Name", "Symbol"], suffixes=("_1", "_2"))

    # Calculate Differences
    merged["Price_Diff"] = merged["Price_1"] - merged["Price_2"]
    merged["Chg_Diff"] = merged["% Chg_1"] - merged["% Chg_2"]

    # Order by Chg_Diff desc
    merged = merged.sort_values(by="Chg_Diff", ascending=False)

    # Show table
    st.subheader("📑 Comparison Result")
    st.dataframe(
        merged[
            ["Stock Name", "Symbol", "Price_1", "Price_2", "Price_Diff", "% Chg_1", "% Chg_2", "Chg_Diff"]
        ]
    )

    # Download button
    st.download_button(
        label="📥 Download Result as Excel",
        data=merged.to_excel(index=False, engine="openpyxl"),
        file_name="comparison_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
