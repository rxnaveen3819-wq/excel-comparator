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

    # Calculate % Difference
    merged["%Chg_Diff"] = merged["%Chg_1"] - merged["%Chg_2"]

    # Calculate Price Difference
    merged["Price_Diff"] = merged["Price_1"] - merged["Price_2"]

    # Show results with Price
    st.subheader("📑 Comparison Result")
    st.dataframe(merged[[
        "Stock Name", 
        "%Chg_1", "%Chg_2", "%Chg_Diff",
        "Price_1", "Price_2", "Price_Diff"
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
        # Sort by % Chg_1 in descending order
merged = merged.sort_values(by="% Chg_1", ascending=False)

# Show results
st.dataframe(merged[["Stock Name", "% Chg_1", "% Chg_2", "Difference", "Price_1", "Price_2", "Price Difference"]])

