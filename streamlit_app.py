import streamlit as st
import pandas as pd

st.title("📊 Excel Comparator")

# Upload two Excel files
file1 = st.file_uploader("Upload First Excel File", type=["xlsx", "xls"])
file2 = st.file_uploader("Upload Second Excel File", type=["xlsx", "xls"])

if file1 and file2:
    # Read Excel files
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Merge on Stock Name
    merged = pd.merge(df1, df2, on="Stock Name", suffixes=("_1", "_2"))

    # Clean %Chg columns (remove % and convert to float)
    merged["%Chg_1"] = merged["%Chg_1"].replace("%", "", regex=True).astype(float)
    merged["%Chg_2"] = merged["%Chg_2"].replace("%", "", regex=True).astype(float)

    # Calculate Difference
    merged["Difference"] = merged["%Chg_1"] - merged["%Chg_2"]

    # Show results with Price
    st.subheader("📑 Comparison Result")
    st.dataframe(merged[[
        "Stock Name", 
        "%Chg_1", "%Chg_2", "Difference",
        "Price_1", "Price_2"
    ]])

    # Download as Excel
    out_file = "comparison_result.xlsx"
    merged.to_excel(out_file, index=False)

    with open(out_file, "rb") as f:
        st.download_button(
            label="📥 Download Result Excel",
            data=f,
            file_name="comparison_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
