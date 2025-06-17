# modules/ui.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.modeling import run_forecast_model, compute_correlation_matrix
def clean_title(name):
    return name.replace(".csv", "").replace("_", " ").title()

import os
import streamlit as st

def configure_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Configuration Panel")

        # --- Market Selection ---
        with st.expander("📍 Market Selection", expanded=True):
            countries = ["US", "UK", "EZ", "CA", "Aussie"]
            country = st.selectbox("🌐 Select Market", countries, help="Choose the country or region for analysis")

        # --- Load Files ---
        folder = os.path.join(".", country)
        files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        if not files:
            st.error("⚠️ No data files found in the selected folder.")
            st.stop()

        # --- Indicator Selection ---
        with st.expander("📊 Indicator Selection", expanded=True):
            search_term = st.text_input("🔍 Filter Indicators", help="Type to filter available indicators")
            filtered_files = [f for f in files if search_term.lower() in f.lower()] if search_term else files

            target_file = st.selectbox("🎯 Target Indicator", filtered_files, help="This is the variable you're trying to predict")
            soft_files = st.multiselect("📎 Soft Indicators", [f for f in filtered_files if f != target_file], help="Indicators used to explain or predict the target")

        # --- Time Filter ---
        with st.expander("🕒 Time Range Filter", expanded=True):
            year_range = st.slider("📅 Select Year Range", 2005, 2025, (2010, 2020), help="Limit the data to this year range")

        # --- Optional Advanced Options ---
        with st.expander("🛠️ Advanced Options (optional)", expanded=False):
            normalize = st.checkbox("📐 Normalize Indicators", value=True, help="Apply standard scaling to soft indicators")
            lag_period = st.slider("⏪ Lag Period", 0, 12, 3, help="Use lagged values of indicators (months)")

        return {
            "country": country,
            "folder": folder,
            "target_file": target_file,
            "soft_files": soft_files,
            "year_range": year_range,
            "normalize": normalize,
            "lag_period": lag_period
        }


def display_tabs(config, df_target, df_softs):
    clean_name = lambda x: x.replace(".csv", "").replace("_", " ").title()

    tabs = st.tabs(["Time Series", "Seasonality", "Forecasting", "Correlation"])

    with tabs[0]:
        st.subheader(f"Actual vs Forecast - {clean_name(config['target_file'])}")
        plot_actual_vs_forecast(df_target, config["target_file"])

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
