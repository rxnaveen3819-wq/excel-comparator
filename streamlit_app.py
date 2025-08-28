import streamlit as st
import pandas as pd

st.title("📊 Excel Comparator with PDF Export")

uploaded_file1 = st.file_uploader("Upload first Excel file", type=["xlsx"])
uploaded_file2 = st.file_uploader("Upload second Excel file", type=["xlsx"])

if uploaded_file1 and uploaded_file2:
    df1 = pd.read_excel(uploaded_file1)
    df2 = pd.read_excel(uploaded_file2)

    # 🔹 Normalize column names
    df1.columns = df1.columns.str.strip().str.lower().str.replace(" ", "_")
    df2.columns = df2.columns.str.strip().str.lower().str.replace(" ", "_")

    required_cols = ["stock_name", "symbol"]

    missing1 = [c for c in required_cols if c not in df1.columns]
    missing2 = [c for c in required_cols if c not in df2.columns]

    if missing1 or missing2:
        st.error(f"❌ Missing columns. File1: {missing1}, File2: {missing2}")
    else:
        merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

        # c
