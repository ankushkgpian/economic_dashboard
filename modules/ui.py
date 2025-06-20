# modules/ui.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.modeling import run_forecast_model, compute_correlation_matrix, compute_lead_lag_correlation
def clean_title(name):
    return name.replace(".csv", "").replace("_", " ").title()

import os
import streamlit as st

def configure_sidebar():
    import os
    with st.sidebar:
        st.markdown("Configuration Panel")

        # --- Target Market Selection ---
        with st.expander("Target Market", expanded=True):
            countries = ["US", "UK", "EZ", "CA", "Aussie"]
            country = st.selectbox("Select Target Market", countries)

        # --- Load Target Indicator Files ---
        target_folder = os.path.join(".", country)
        target_files = [f for f in os.listdir(target_folder) if f.endswith(".csv")]
        if not target_files:
            st.error("No target indicators found in selected market.")
            st.stop()
        target_file = st.selectbox("Target Indicator", target_files)

        # --- Soft Indicators from All Markets ---
        with st.expander("📎 Select Soft Indicators from All Markets", expanded=True):
            all_soft_options = {}
            for m in countries:
                folder = os.path.join(".", m)
                try:
                    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
                    options = [f"{m}/{f}" for f in files if f != target_file or m != country]
                    if options:
                        selected = st.multiselect(f"{m} Soft Indicators", options, default=[], key=m)
                        all_soft_options[m] = selected
                except FileNotFoundError:
                    continue

            # Flatten selections
            soft_files = [item for sublist in all_soft_options.values() for item in sublist]

        # --- Time Filter ---
        with st.expander("🕒 Time Range Filter", expanded=True):
            year_range = st.slider("Select Year Range", 2005, 2025, (2010, 2020))

        # --- Advanced Options ---
        with st.expander("🛠Advanced Options", expanded=False):
            normalize = st.checkbox("Normalize Indicators", value=True)
            lag_period = st.slider("Lag Period", 0, 12, 3)

        return {
            "country": country,
            "folder": target_folder,
            "target_file": target_file,
            "soft_files": soft_files,
            "year_range": year_range,
            "normalize": normalize,
            "lag_period": lag_period
        }

def display_tabs(config, df_target, df_softs):
    clean_name = lambda x: x.replace(".csv", "").replace("_", " ").title()

    tabs = st.tabs(["Time Series", "Seasonality", "Forecasting", "Correlation Matrix", "Lead-Lag"])

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
        compute_correlation_matrix(df_target, df_softs, config)

    with tabs[4]:
        st.subheader("Intermarket Lead-Lag Correlation")
        
        countries = ["US", "UK", "EZ", "CA", "Aussie"]
        country1 = st.selectbox("Select Country for Indicator 1", countries, key="leadlag1")
        country2 = st.selectbox("Select Country for Indicator 2", countries, key="leadlag2")
    
        # Load indicator files
        folder1 = os.path.join(".", country1)
        folder2 = os.path.join(".", country2)
        file1 = st.selectbox("Indicator 1", os.listdir(folder1), key="file1")
        file2 = st.selectbox("Indicator 2", os.listdir(folder2), key="file2")
    
        df1 = pd.read_csv(os.path.join(folder1, file1), parse_dates=["Reference Period"])
        df2 = pd.read_csv(os.path.join(folder2, file2), parse_dates=["Reference Period"])
    
        lag_q = st.slider("Lag (quarters)", 0, 8, 3)
        compute_lead_lag_correlation(df1, df2, lag_quarters=lag_q)

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
