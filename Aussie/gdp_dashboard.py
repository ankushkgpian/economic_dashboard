import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

# --- Streamlit Setup ---
st.set_page_config(page_title="GDP Prediction Dashboard", layout="wide")
st.title("📊 Real GDP Prediction using Soft Indicators (2014–2017)")

# --- Configuration ---
folder_path = "."  # Assuming CSVs are in the same directory

# Soft indicators
files = {
    "Westpac Consumer Sentiment Index sa": "Westpac_Consumer_Sentiment_Index_sa_economic_data.csv",
    "AIG Performance of Manufacturing Index": "AIG_Performance_of_Manufacturing_Index_economic_data.csv",
    "ANZ Job Advertisements mom": "ANZ_Job_Advertisements_mom_economic_data.csv",
    "NAB Business Confidence Index": "NAB_Business_Confidence_Index_economic_data.csv",
    "OECD Australia Leading Indicator yoy": "OECD_Australia_Leading_Indicator_yoy_economic_data.csv"
}

target_file = "Real_GDP_qoq__sa_economic_data.csv"
target_name = "Real GDP qoq  sa"

# --- Load Indicator Function ---
@st.cache_data
def load_indicator(file_name, name):
    df = pd.read_csv(os.path.join(folder_path, file_name))
    df['Reference Period'] = pd.to_datetime(df['Reference Period'], errors='coerce')
    df = df[['Reference Period', 'Actual']].rename(columns={'Actual': name})
    return df

# Load soft indicators
indicator_dfs = [load_indicator(f, name) for name, f in files.items()]

# Merge all indicators
merged_df = indicator_dfs[0]
for df in indicator_dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='Reference Period', how='inner')

# Load target GDP data
target_df = load_indicator(target_file, 'Target')
data = pd.merge(merged_df, target_df, on='Reference Period', how='inner')

# Filter for years 2014–2017
data = data[(data['Reference Period'].dt.year >= 2014) & (data['Reference Period'].dt.year <= 2017)]
data = data.dropna()

# --- Modeling ---
X = data[list(files.keys())]
y = data['Target']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LinearRegression()
model.fit(X_scaled, y)
y_pred = model.predict(X_scaled)

# 95% prediction interval
residuals = y - y_pred
std_err = np.std(residuals)
interval = 1.96 * std_err

# --- Display Indicator Weights ---
st.subheader("📌 Indicator Weights in Predicting GDP")
coef_df = pd.DataFrame({
    "Indicator": list(files.keys()),
    "Weight": model.coef_
}).sort_values(by="Weight", ascending=False)

st.dataframe(coef_df, use_container_width=True)

# --- Plot: Actual vs Predicted GDP ---
st.subheader("📈 Actual vs Predicted GDP (Interactive)")

fig = go.Figure()

# Actual GDP
fig.add_trace(go.Scatter(
    x=data['Reference Period'],
    y=y,
    mode='lines+markers',
    name='Actual GDP',
    line=dict(color='blue'),
    marker=dict(size=6)
))

# Predicted GDP
fig.add_trace(go.Scatter(
    x=data['Reference Period'],
    y=y_pred,
    mode='lines+markers',
    name='Predicted GDP',
    line=dict(color='orange', dash='dash'),
    marker=dict(symbol='x', size=6)
))

# 95% Confidence Interval
# 95% Confidence Interval
fig.add_trace(go.Scatter(
    x=pd.concat([
        data['Reference Period'],
        data['Reference Period'][::-1]
    ]),
    y=pd.concat([
        pd.Series(y_pred + interval),
        pd.Series((y_pred - interval)[::-1])
    ]),
    fill='toself',
    fillcolor='rgba(128, 128, 128, 0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=True,
    name='95% Prediction Interval'
))

fig.update_layout(
    title="Interactive GDP Prediction Range (2014–2017)",
    xaxis_title="Reference Period",
    yaxis_title="Real GDP QoQ SA (%)",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# --- Optional: Show full dataset ---
with st.expander("🔎 Show Full Dataset"):
    st.dataframe(data.reset_index(drop=True), use_container_width=True)
