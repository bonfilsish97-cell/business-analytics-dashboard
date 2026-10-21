"""Business Analytics Dashboard - minimum working version (Step 1).
Run with:  streamlit run app.py
"""
import io
from datetime import date

import pandas as pd
import streamlit as st

from utils.data_loader import DataLoadError, list_sheets, load_dataframe, column_summary, quality_summary, get_extension
from utils.analysis import numeric_columns, category_columns, date_columns, AGGREGATIONS
from utils.visualizations import build_chart, CHART_TYPES

st.set_page_config(page_title="Business Analytics Dashboard", page_icon="📊", layout="wide")

# Light blue/white/neutral styling for KPI cards
st.markdown("""
<style>
[data-testid="stMetric"] {background:#F4F8FD; border:1px solid #D6E4F5; border-radius:10px; padding:12px 16px;}
h1, h2, h3 {color:#1F4E9E;}
</style>""", unsafe_allow_html=True)

SAMPLE_PATH = "data/sample_business_data.csv"


# ---------- Sidebar: data source ----------
st.sidebar.title("📊 Analytics Dashboard")
page = st.sidebar.radio("Navigate", ["Overview", "Data Preview", "Summary Statistics", "Charts", "Download"])
st.sidebar.divider()
uploaded = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
use_sample = st.sidebar.checkbox("Use synthetic sample data", value=uploaded is None)

df, source_name = None, None
try:
    if uploaded is not None:
        raw = uploaded.getvalue()
        sheet = None
        if get_extension(uploaded.name) in (".xlsx", ".xls"):
            sheets = list_sheets(raw)
            sheet = st.sidebar.selectbox("Worksheet", sheets) if len(sheets) > 1 else sheets[0]
        with st.spinner("Loading data..."):
            df, source_name = load_dataframe(raw, uploaded.name, sheet), uploaded.name
    elif use_sample:
        with open(SAMPLE_PATH, "rb") as f:
            df, source_name = load_dataframe(f.read(), "sample_business_data.csv"), "Synthetic sample data"
except DataLoadError as err:
    st.error(f"⚠️ {err}")
except FileNotFoundError:
    st.error("Sample file not found. Run `python make_sample_data.py` first.")

if df is None:
    st.title("Business Analytics Dashboard")
    st.info("Upload a CSV or Excel file in the sidebar to get started.")
    st.stop()

nums, cats, dates = numeric_columns(df), category_columns(df), date_columns(df)


# ---------- Pages ----------
if page == "Overview":
    st.title("Business Analytics Dashboard")
    st.caption("Upload business data, explore it, build charts and download results. Works with any tabular dataset.")
    q = quality_summary(df)
    st.subheader(f"Dataset: {source_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{q['rows']:,}")
    c2.metric("Columns", q["columns"])
    c3.metric("Missing cells", f"{q['missing_cells']:,}", f"{q['missing_pct']}% of all cells", delta_color="off")
    c4.metric("Duplicate rows", q["duplicate_rows"])
    if nums:
        st.subheader("Key figures (numeric columns)")
        cols = st.columns(min(4, len(nums)))
        for col, name in zip(cols, nums[:4]):
            col.metric(f"Total {name}", f"{df[name].sum():,.2f}", f"avg {df[name].mean():,.2f}", delta_color="off")

elif page == "Data Preview":
    st.title("Data Preview")
    st.write(f"**{df.shape[0]:,} rows × {df.shape[1]} columns**")
    st.dataframe(df.head(50), use_container_width=True)
    st.subheader("Columns and data types")
    st.dataframe(column_summary(df), use_container_width=True, hide_index=True)

elif page == "Summary Statistics":
    st.title("Summary Statistics")
    if nums:
        st.subheader("Numeric columns")
        st.dataframe(df[nums].describe().T.round(2), use_container_width=True)
    else:
        st.info("No numeric columns found.")
    if cats:
        st.subheader("Categorical columns")
        st.dataframe(df[cats].describe().T, use_container_width=True)

elif page == "Charts":
    st.title("Interactive Charts")
    c1, c2 = st.columns(2)
    chart = c1.selectbox("Chart type", CHART_TYPES)
    agg = c2.selectbox("Aggregation (bar / line / pie)", list(AGGREGATIONS))
    all_cols = df.columns.tolist()
    c3, c4, c5 = st.columns(3)
    x = c3.selectbox("X axis", all_cols)
    y = c4.selectbox("Y axis", nums if nums else all_cols)
    group = c5.selectbox("Group / colour by", ["(none)"] + cats)
    group = None if group == "(none)" else group
    try:
        with st.spinner("Building chart..."):
            fig = build_chart(df, chart, x, y, group, agg)
        st.plotly_chart(fig, use_container_width=True)
    except ValueError as err:
        st.warning(f"⚠️ {err}")

elif page == "Download":
    st.title("Download Data")
    st.caption(f"Report date: {date.today():%Y-%m-%d}  |  Source: {source_name}")
    st.download_button("⬇️ Download as CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name=f"processed_data_{date.today():%Y%m%d}.csv", mime="text/csv")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    st.download_button("⬇️ Download as Excel", buf.getvalue(),
                       file_name=f"processed_data_{date.today():%Y%m%d}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
