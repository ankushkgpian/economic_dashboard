# modules/modeling.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run_forecast_model(df_target, df_softs, config):
    if not df_softs:
        st.warning("Select at least one soft indicator.")
        return

    # Base dataframe with target
    df = df_target[["Reference Period", "Actual"]].rename(columns={"Actual": "Target"})
    feature_columns = []

    for i, soft_df in enumerate(df_softs):
        # Try to extract file name from config
        try:
            name = config["soft_sources"][i]["file"].replace(".csv", "")
        except Exception:
            name = f"Soft_{i+1}"

        # Rename and merge
        soft_col = name
        df = df.merge(
            soft_df[["Reference Period", "Actual"]].rename(columns={"Actual": soft_col}),
            on="Reference Period",
            how="inner"
        )

        feature_columns.append(soft_col)

    # Create lag and diff features
    lag_period = config.get("lag_period", 1)
    df.sort_values("Reference Period", inplace=True)
    full_feature_names = []

    for col in feature_columns:
        if col in df.columns:
            lag_name = f"{col}_lag1"
            diff_name = f"{col}_diff1"
            df[lag_name] = df[col].shift(lag_period)
            df[diff_name] = df[col].diff()
            full_feature_names.extend([lag_name, diff_name])
        else:
            st.warning(f"Column `{col}` not found in merged data. Skipping lag/diff creation.")

    df.dropna(inplace=True)

    # Define X and y
    X = df[full_feature_names]
    y = df["Target"]

    # Save column names before scaling
    feature_names = X.columns.tolist()

    # Normalize if selected
    if config.get("normalize", True):
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)

    # --- Model Metrics ---
    st.markdown("#### 📊 Model Metrics")
    st.table(pd.DataFrame({
        "Metric": ["R²", "MAE", "RMSE"],
        "Value": [round(r2_score(y, y_pred), 4),
                  round(mean_absolute_error(y, y_pred), 4),
                  round(np.sqrt(mean_squared_error(y, y_pred)), 4)]
    }))

    # --- Actual vs Predicted Plot ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Reference Period"], y=y, name="Actual"))
    fig.add_trace(go.Scatter(x=df["Reference Period"], y=y_pred, name="Predicted"))
    fig.update_layout(title="Actual vs Predicted", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # --- Feature Importances ---
    importances_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False).head(10)

    fig = px.bar(importances_df, x="Importance", y="Feature", orientation="h", title="Top 10 Feature Importances")
    st.plotly_chart(fig, use_container_width=True)

    # --- Feature Mapping Table ---
    st.markdown("#### 🔍 Feature Name Mapping")
    mapping_df = pd.DataFrame({
        "Feature Name": feature_names,
        "Base Indicator": [name.split("_")[0] for name in feature_names],
        "Transformation": [name.split("_")[1] if "_" in name else "" for name in feature_names]
    })

    st.dataframe(mapping_df, use_container_width=True)


def compute_correlation_matrix(df_target, df_softs):
    if not df_softs:
        st.warning("Select soft indicators.")
        return

    df_corr = df_target[["Reference Period", "Actual"]].rename(columns={"Actual": "Target"})
    soft_names = []
    for soft_df, path in zip(df_softs, config["soft_files"]):
        name = path.split("/")[-1].replace(".csv", "")
        soft_names.append(name)
        df_corr = df_corr.merge(soft_df[["Reference Period", "Actual"]].rename(columns={"Actual": name}),
                                on="Reference Period", how="inner")

    corr = df_corr.drop(columns="Reference Period").corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu", aspect="auto")
    fig.update_layout(height=800, width=1200, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # --- Show indicator names mapping ---
    st.markdown("##### 🧾 Indicator Abbreviations")
    mapping_df = pd.DataFrame({
        "Variable": ["Target"] + soft_names,
        "Source File": [config["target_file"].replace(".csv", "")] + [f.split('/')[-1].replace(".csv", "") for f in config["soft_files"]]
    })
    st.dataframe(mapping_df, use_container_width=True)


def compute_lead_lag_correlation(indicator1_df, indicator2_df, lag_quarters=3):
    # Merge two time series on Reference Period
    df1 = indicator1_df[["Reference Period", "Actual"]].copy()
    df2 = indicator2_df[["Reference Period", "Actual"]].copy()

    df1.rename(columns={"Actual": "Indicator1"}, inplace=True)
    df2.rename(columns={"Actual": "Indicator2"}, inplace=True)

    # Shift Indicator1 by specified lag (quarters * 3 months if monthly data)
    df1["Reference Period"] = df1["Reference Period"] + pd.DateOffset(months=lag_quarters * 3)

    # Merge on shifted period
    merged = pd.merge(df1, df2, on="Reference Period", how="inner")

    if merged.empty:
        st.warning("No overlapping periods after lagging.")
        return

    corr = merged["Indicator1"].corr(merged["Indicator2"])
    st.markdown(f"### Lead-Lag Correlation: {round(corr, 3)}")
    st.write(f"Correlation after shifting Indicator 1 by {lag_quarters} quarters.")

    # Plot the two time series
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged["Reference Period"], y=merged["Indicator1"], name="Indicator 1 (Lagged)"))
    fig.add_trace(go.Scatter(x=merged["Reference Period"], y=merged["Indicator2"], name="Indicator 2"))
    fig.update_layout(title="Lead-Lag Comparison", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
