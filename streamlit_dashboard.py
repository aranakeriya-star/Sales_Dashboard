# streamlit_dashboard.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Bata Sales Dashboard", layout="wide")
st.title("Bata Sales Dashboard")

st.markdown("This dashboard loads the repo CSV `Bata Data.csv` by default. You can also upload a different CSV file.")

use_repo_csv = st.checkbox("Load repo's Bata Data.csv (recommended)", value=True)
uploaded = st.file_uploader("Or upload a CSV file (optional)", type=["csv"])

df = None
if use_repo_csv:
    try:
        df = pd.read_csv("Bata Data.csv")
    except Exception as e:
        st.error(f"Could not load Bata Data.csv from repo: {e}")

if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        df = uploaded_df
        st.success("Loaded uploaded CSV")
    except Exception as e:
        st.error(f"Failed to parse uploaded CSV: {e}")

if df is None:
    st.info("No data loaded yet. Upload a CSV or enable 'Load repo's Bata Data.csv'.")
else:
    st.sidebar.header("Controls")
    cols = df.columns.tolist()
    x_col = st.sidebar.selectbox("X axis (choose a column)", options=cols, index=0)
    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    selected = st.sidebar.multiselect("Y series (numeric)", options=numeric_cols, default=numeric_cols[:2])

    st.sidebar.markdown("---")
    st.sidebar.write(f"Rows: {len(df)}  Columns: {len(cols)}")

    st.subheader("Data preview")
    st.dataframe(df.head(200))

    if selected:
        st.subheader("Line chart")
        chart_df = df.copy()
        chart_df[x_col] = chart_df[x_col].astype(str)
        layers = []
        base = alt.Chart(chart_df).encode(x=alt.X(x_col, type='ordinal' if chart_df[x_col].dtype == 'object' else 'quantitative'))
        for c in selected:
            layers.append(base.mark_line(point=True).encode(y=alt.Y(c, type='quantitative'), tooltip=cols))
        chart = alt.layer(*layers).interactive().properties(height=400)
        st.altair_chart(chart, use_container_width=True)

    st.subheader("Download data")
    st.download_button("Download current data as CSV", df.to_csv(index=False), file_name="export.csv", mime="text/csv")
