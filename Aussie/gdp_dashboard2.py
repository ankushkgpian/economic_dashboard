import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
# --- Page Setup ---
st.set_page_config(page_title="Economic Dashboard", layout="wide")
st.title("Australian Economic Dashboard (2014–2017)")

folder_path = "."



# --- Plot 1: Normalized Tier 1 Indicators ---
st.header("📉 Tier 1 Economic Indicators (Normalized)")

@st.cache_data
def load_tier1_plot():
    tier1_indicators = [
        'Real GDP qoq sa', 'Nominal GDP qoq sa',
        'Consumer Price Index qoq', 'Consumer Price Index yoy',
        'RBA Trimmed Mean Core CPI qoq sa', 'RBA Trimmed Mean Core CPI yoy sa',
        'Unemployment Rate sa', 'Total Employed Change 000s mom sa',
        'Retail Sales mom sa', 'Retail Sales yoy sa',
        'Trade Balance AUD bn', 'Exports AUD bn', 'Imports AUD bn',
        'Westpac Consumer Sentiment Index sa', 'NAB Business Conditions Index'
    ]
    economic_data = {}
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            name = file.replace("_economic_data.csv", "").replace("_", " ")
            df = pd.read_csv(os.path.join(folder_path, file))
            for col in ['Reference Period', 'Release Date']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            economic_data[name] = df

    combined = pd.DataFrame()
    for indicator in tier1_indicators:
        if indicator in economic_data:
            df = economic_data[indicator].copy()
            date_col = 'Reference Period' if 'Reference Period' in df.columns else 'Release Date'
            df = df[[date_col, 'Actual']].dropna()
            df = df.rename(columns={date_col: 'Date', 'Actual': indicator}).set_index('Date')
            combined = combined.join(df, how='outer') if not combined.empty else df

    combined = combined.sort_index().loc['2014':'2017'].dropna(how='all')
    scaler = StandardScaler()
    normalized = pd.DataFrame(scaler.fit_transform(combined), columns=combined.columns, index=combined.index)

    fig = go.Figure()
    for col in normalized.columns:
        fig.add_trace(go.Scatter(x=normalized.index, y=normalized[col], mode='lines', name=col))
    fig.update_layout(
        title='Normalized Tier 1 Indicators (Z-Score, 2014–2017)',
        xaxis_title='Date', yaxis_title='Z-score',
        hovermode='x unified', height=600
    )
    return fig

fig1 = load_tier1_plot()
st.plotly_chart(fig1, use_container_width=True)

# --- Plot 2: GDP Components ---
st.header("GDP & Economic Activity Breakdown")

@st.cache_data
def load_gdp_components_plot():
    files = {
        "Real GDP qoq sa": "Real_GDP_qoq__sa_economic_data.csv",
        "Nominal GDP qoq sa": "Nominal_GDP_qoq__sa_economic_data.csv",
        "Final Domestic Demand qoq sa": "Final_Domestic_Demand_qoq__sa_economic_data.csv",
        "Gross Fixed Capital Investment qoq sa": "Gross_Fixed_Capital_Investment_qoq__sa_economic_data.csv",
        "Government Consumption qoq sa": "Government_Consumption_qoq__sa_economic_data.csv",
    }
    data = {}
    for name, fname in files.items():
        df = pd.read_csv(os.path.join(folder_path, fname))
        date_col = 'Reference Period' if 'Reference Period' in df.columns else 'Release Date'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[[date_col, 'Actual']].dropna()
        df = df.rename(columns={date_col: 'Date', 'Actual': name})
        df = df.set_index('Date').sort_index()
        df = df.loc['2014':'2017']
        data[name] = df
    combined = pd.concat(data.values(), axis=1, join='inner')

    fig = go.Figure()
    for col in combined.columns:
        fig.add_trace(go.Scatter(x=combined.index, y=combined[col], mode='lines+markers', name=col))
    fig.update_layout(
        title='GDP & Economic Activity (2014–2017)',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified',
        height=600
    )
    return fig

fig2 = load_gdp_components_plot()
st.plotly_chart(fig2, use_container_width=True)

# --- Plot 3: Inflation Overview ---
st.header("Inflation Trends (2014–2017)")

@st.cache_data
def load_inflation_plot():
    files = {
        "Consumer Price Index qoq": "Consumer_Price_Index_qoq_economic_data.csv",
        "Consumer Price Index yoy": "Consumer_Price_Index_yoy_economic_data.csv",
        "RBA Trimmed Mean Core CPI qoq sa": "RBA_Trimmed_Mean_Core_CPI_qoq__sa_economic_data.csv",
        "RBA Trimmed Mean Core CPI yoy sa": "RBA_Trimmed_Mean_Core_CPI_yoy__sa_economic_data.csv",
        "RBA Weighted Median CPI qoq sa": "RBA_Weighted_Median_CPI_qoq__sa_economic_data.csv",
        "RBA Weighted Median CPI yoy sa": "RBA_Weighted_Median_CPI_yoy__sa_economic_data.csv",
    }

    data = {}
    for name, fname in files.items():
        df = pd.read_csv(os.path.join(folder_path, fname))
        date_col = 'Reference Period' if 'Reference Period' in df.columns else 'Release Date'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[[date_col, 'Actual']].dropna()
        df = df.rename(columns={date_col: 'Date', 'Actual': name})
        df = df.set_index('Date').sort_index()
        df = df.loc['2014':'2017']
        data[name] = df
    combined = pd.concat(data.values(), axis=1, join='inner')

    fig = go.Figure()
    for col in combined.columns:
        fig.add_trace(go.Scatter(x=combined.index, y=combined[col],
                                 mode='lines+markers', name=col))

    fig.update_layout(
        title='Inflation Indicators (2014–2017)',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified',
        height=600
    )
    return fig

fig3 = load_inflation_plot()
st.plotly_chart(fig3, use_container_width=True)


# --- Plot 4: Business Confidence & Investment ---
st.header("Business Confidence & Investment (2014–2017)")

@st.cache_data
def load_business_confidence_plot():
    files = {
        "NAB Business Confidence Index": "NAB_Business_Confidence_Index_economic_data.csv",
        "NAB Business Conditions Index": "NAB_Business_Conditions_Index_economic_data.csv",
        "ANZ Job Advertisements mom": "ANZ_Job_Advertisements_mom_economic_data.csv",
        "Private Sector Credit yoy": "Private_Sector_Credit_yoy_economic_data.csv",
    }

    data = {}
    for name, fname in files.items():
        df = pd.read_csv(os.path.join(folder_path, fname))
        date_col = 'Reference Period' if 'Reference Period' in df.columns else 'Release Date'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[[date_col, 'Actual']].dropna()
        df = df.rename(columns={date_col: 'Date', 'Actual': name})
        df = df.set_index('Date').sort_index()
        df = df.loc['2014':'2017']
        data[name] = df
    combined = pd.concat(data.values(), axis=1, join='inner')

    fig = go.Figure()
    for col in combined.columns:
        fig.add_trace(go.Scatter(x=combined.index, y=combined[col],
                                 mode='lines+markers', name=col))

    fig.update_layout(
        title='Business Confidence & Investment Indicators (2014–2017)',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified',
        height=600
    )
    return fig

fig4 = load_business_confidence_plot()
st.plotly_chart(fig4, use_container_width=True)

# --- Plot 5: Consumer & Housing ---
st.header("Consumer & Housing (2014–2017)")

@st.cache_data
def load_consumer_housing_plot():
    files = {
        "Retail Sales mom sa": "Retail_Sales_mom__sa_economic_data.csv",
        "Retail Sales yoy sa": "Retail_Sales_yoy__sa_economic_data.csv",
        "House Price Index for Established Homes yoy": "House_Price_Index_for_Established_Homes_yoy_economic_data.csv",
        "Building Approvals for Total Dwelling Units yoy sa": "Building_Approvals_for_Total_Dwelling_Units_yoy__sa_economic_data.csv",
    }

    data = {}
    for name, fname in files.items():
        df = pd.read_csv(os.path.join(folder_path, fname))
        date_col = 'Reference Period' if 'Reference Period' in df.columns else 'Release Date'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df[[date_col, 'Actual']].dropna()
        df = df.rename(columns={date_col: 'Date', 'Actual': name})
        df = df.set_index('Date').sort_index()
        df = df.loc['2014':'2017']
        data[name] = df
    combined = pd.concat(data.values(), axis=1, join='inner')

    fig = go.Figure()
    for col in combined.columns:
        fig.add_trace(go.Scatter(x=combined.index, y=combined[col],
                                 mode='lines+markers', name=col))

    fig.update_layout(
        title='Consumer & Housing Indicators (2014–2017)',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified',
        height=600
    )
    return fig

fig5 = load_consumer_housing_plot()
st.plotly_chart(fig5, use_container_width=True)


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

# Load indicators
indicator_dfs = [load_indicator(f, name) for name, f in files.items()]
merged_df = indicator_dfs[0]
for df in indicator_dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='Reference Period', how='inner')

# Load target GDP data
target_df = load_indicator(target_file, 'Target')
data = pd.merge(merged_df, target_df, on='Reference Period', how='inner')

# Filter for 2014–2017
data = data[(data['Reference Period'].dt.year >= 2014) & (data['Reference Period'].dt.year <= 2017)]
data = data.sort_values('Reference Period').reset_index(drop=True)

# --- Feature Engineering: Lag and Difference ---
for col in files.keys():
    data[f"{col}_lag1"] = data[col].shift(1)
    data[f"{col}_diff1"] = data[col].diff()

data = data.dropna().reset_index(drop=True)

# --- Modeling ---
feature_cols = [col for col in data.columns if col not in ['Reference Period', 'Target']]
X = data[feature_cols]
y = data['Target']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_scaled, y)
y_pred = model.predict(X_scaled)

# --- Metrics ---
residuals = y - y_pred
std_err = np.std(residuals)
interval = 1.96 * std_err

r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))

# --- Display Performance ---
st.title("Australian GDP Prediction Using Soft Indicators")
st.markdown(f"**R² Score:** `{r2:.4f}` &nbsp;&nbsp; | &nbsp;&nbsp; **MAE:** `{mae:.4f}` &nbsp;&nbsp; | &nbsp;&nbsp; **RMSE:** `{rmse:.4f}`")

# --- Feature Importance ---
importances = model.feature_importances_
importance_df = pd.DataFrame({
    "Feature": feature_cols,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

st.subheader("Top Feature Importances (weight given)")
st.dataframe(importance_df.head(10), use_container_width=True)

# --- Plot: Actual vs Predicted GDP ---
st.subheader("Actual vs Predicted Real GDP (Interactive)")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=data['Reference Period'],
    y=y,
    mode='lines+markers',
    name='Actual GDP',
    line=dict(color='blue'),
    marker=dict(size=6)
))

fig.add_trace(go.Scatter(
    x=data['Reference Period'],
    y=y_pred,
    mode='lines+markers',
    name='Predicted GDP',
    line=dict(color='orange', dash='dash'),
    marker=dict(symbol='x', size=6)
))

fig.add_trace(go.Scatter(
    x=pd.concat([data['Reference Period'], data['Reference Period'][::-1]]),
    y=pd.concat([pd.Series(y_pred + interval), pd.Series((y_pred - interval)[::-1])]),
    fill='toself',
    fillcolor='rgba(128, 128, 128, 0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=True,
    name='95% Prediction Interval'
))

fig.update_layout(
    title="Real GDP QoQ SA – Actual vs Predicted (2014–2017)",
    xaxis_title="Reference Period",
    yaxis_title="GDP Growth (%)",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)


# Optional: Raw Data
with st.expander("📄 Show Full Merged Dataset for GDP Prediction"):
    st.dataframe(data.reset_index(drop=True))
