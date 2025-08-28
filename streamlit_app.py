import streamlit as st
import pandas as pd

st.title("📊 Excel Comparator App")

# Upload two Excel files
uploaded_file1 = st.file_uploader("Upload first Excel file", type=["xlsx"])
uploaded_file2 = st.file_uploader("Upload second Excel file", type=["xlsx"])

if uploaded_file1 and uploaded_file2:
    # Read Excel files
    df1 = pd.read_excel(uploaded_file1)
    df2 = pd.read_excel(uploaded_file2)

    # 🔍 Debug: Show column names to user
    st.subheader("File 1 Columns")
    st.write(df1.columns.tolist())

    st.subheader("File 2 Columns")
    st.write(df2.columns.tolist())

    # ⚠️ At this point we don't know exact column names
    # Once you confirm the correct names, we will update this merge line
    try:
        merged = pd.merge(df1, df2, on=["stock_name", "symbol"], suffixes=("_1", "_2"))

        # Calculate differences
        merged["chg_diff"] = merged["chg_1"] - merged["chg_2"]
        merged["price_diff"] = merged["price_1"] - merged["price_2"]

        # Sort by chg_diff descending
        merged = merged.sort_values(by="chg_diff", ascending=False)

        # Show final comparison table
        st.subheader("Comparison Result")
        st.dataframe(merged)

        # Download button
        st.download_button(
            label="📥 Download Comparison",
            data=merged.to_csv(index=False).encode("utf-8"),
            file_name="comparison.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"⚠️ Merge failed: {e}")
        st.info("Please check the column names shown above and update merge keys.")
