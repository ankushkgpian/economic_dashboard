# modules/ui.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.modeling import run_forecast_model, compute_correlation_matrix
def clean_title(name):
    return name.replace(".csv", "").replace("_", " ").title()

def configure_sidebar():
    with st.sidebar:
        st.header("Configuration")
        countries = ["US", "UK", "EZ", "CA", "Aussie"]
        country = st.selectbox("Select Market", countries)

        import os
        folder = os.path.join(".", country)
        files = [f for f in os.listdir(folder) if f.endswith(".csv")]

        if not files:
            st.error("No files found.")
            st.stop()

        target_file = st.selectbox("Target Indicator", files)
        soft_files = st.multiselect("Select Soft Indicators", [f for f in files if f != target_file])

        st.header("Time Filter")
        year_range = st.slider("Select Years", 2005, 2025, (2010, 2020))

        return {
            "country": country,
            "folder": folder,
            "target_file": target_file,
            "soft_files": soft_files,
            "year_range": year_range
        }

def display_tabs(config, df_target, df_softs):
    clean_name = lambda x: x.replace(".csv", "").replace("_", " ").title()

    tabs = st.tabs(["Time Series", "Seasonality", "Forecasting", "Correlation"])

    with tabs[0]:
        st.subheader(f"Actual vs Forecast - {clean_name(config['target_file'])}")
        plot_actual_vs_forecast(df_target)

    with tabs[1]:
        st.subheader("Surprise Seasonality")
        plot_seasonality(df_target)

    with tabs[2]:
        st.subheader("Prediction Using Soft Indicators")
        run_forecast_model(df_target, df_softs, config)

    with tabs[3]:
        st.subheader("Correlation Matrix")
        compute_correlation_matrix(df_target, df_softs)

    st.markdown("""
        <style>
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: 16px;
                font-weight: 600;
                padding: 8px 24px;
            }
            h2, h3 {
                color: #0B5394;
            }
            .stButton>button {
                background-color: #0B5394;
                color: white;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)


def plot_actual_vs_forecast(df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Reference Period"], y=df["Actual"], name="Actual", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=df["Reference Period"], y=df["Median_Forecast"], name="Forecast", mode="lines+markers", line=dict(dash="dash")))
    fig.update_layout(template="plotly_white", title=title.replace(".csv", ""), height=400)
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonality(df):
    df["Month"] = df["Reference Period"].dt.month
    month_avg = df.groupby("Month")["Surprise"].mean().reset_index()
    month_map = {i: m for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
    month_avg["Month"] = month_avg["Month"].map(month_map)
    fig = px.bar(month_avg, x="Month", y="Surprise", title="Average Surprise by Month", color="Surprise", color_continuous_scale="Blues")
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

def download_options(df, filename):
    st.download_button("Download CSV", df.to_csv(index=False), file_name=filename)
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("Download Excel", buffer.getvalue(), file_name=filename.replace(".csv", ".xlsx"))
