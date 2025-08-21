import streamlit as st
import pandas as pd

st.title("📊 Excel Comparator App")

# Upload two Excel files
file1 = st.file_uploader("Upload first Excel file", type=["xlsx", "xls"])
file2 = st.file_uploader("Upload second Excel file", type=["xlsx", "xls"])

if file1 and file2:
    # Read Excel files
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Standardize column names (strip spaces, lower case)
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()

    # Merge on stock name
    merged = pd.merge(df1, df2, on="stock name", suffixes=("_1", "_2"))

    # Convert %Chg to numeric
    merged["%chg_1"] = merged["%chg_1"].str.replace("%", "").astype(float)
    merged["%chg_2"] = merged["%chg_2"].str.replace("%", "").astype(float)

    # Calculate Differences
    merged["Difference"] = merged["%chg_1"] - merged["%chg_2"]
    merged["Price Difference"] = merged["price_1"] - merged["price_2"]

    # Sort by %chg_1 (descending)
    merged = merged.sort_values(by="%chg_1", ascending=False)

    # Show results
    st.subheader("📑 Comparison Result")
    st.dataframe(merged[["stock name", "%chg_1", "%chg_2", "Difference",
                         "price_1", "price_2", "Price Difference"]])

    # Download button
    st.download_button(
        label="📥 Download Result as Excel",
        data=merged.to_excel(index=False, engine="openpyxl"),
        file_name="comparison_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
