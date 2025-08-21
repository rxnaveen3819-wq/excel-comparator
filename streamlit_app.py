import streamlit as st
import pandas as pd

st.title("📊 Excel %Chg Comparator")

uploaded_file1 = st.file_uploader("Upload Excel 1", type=["csv", "xlsx"])
uploaded_file2 = st.file_uploader("Upload Excel 2", type=["csv", "xlsx"])

if uploaded_file1 and uploaded_file2:
    df1 = pd.read_excel(uploaded_file1) if uploaded_file1.name.endswith("xlsx") else pd.read_csv(uploaded_file1)
    df2 = pd.read_excel(uploaded_file2) if uploaded_file2.name.endswith("xlsx") else pd.read_csv(uploaded_file2)

    # Normalize column names
    df1 = df1.rename(columns=lambda x: x.strip().lower())
    df2 = df2.rename(columns=lambda x: x.strip().lower())

# Merge on stock name
merged = pd.merge(df1, df2, on="Stock Name", suffixes=("_1", "_2"))

# Clean %Chg columns and calculate Difference
merged["%Chg_1"] = merged["%Chg_1"].replace("%","", regex=True).astype(float)
merged["%Chg_2"] = merged["%Chg_2"].replace("%","", regex=True).astype(float)
merged["Difference"] = merged["%Chg_1"] - merged["%Chg_2"]

    st.dataframe(merged[["stock Name", "% chg_1", "% chg_2", "Difference"]])

    st.download_button(
        "📥 Download CSV",
        merged.to_csv(index=False),
        "comparison.csv",
        "text/csv"
    )
