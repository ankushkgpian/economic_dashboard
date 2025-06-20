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
        # Use file name or fallback to Soft_1, Soft_2...
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

    for col in feature_columns:
        if col in df.columns:
            df[f"{col}_lag1"] = df[col].shift(lag_period)
            df[f"{col}_diff1"] = df[col].diff()
        else:
            st.warning(f"Column `{col}` not found in merged data. Skipping lag/diff creation.")

    df.dropna(inplace=True)

    X = df.drop(columns=["Reference Period", "Target"])
    y = df["Target"]

    if config.get("normalize", True):
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)

    # --- Metrics ---
    st.markdown("#### Model Metrics")
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
    st.plotly_chart(fig, use_container_width=True)

    # --- Feature Importances ---
    importances_df = pd.DataFrame({
        "Feature": X.columns if isinstance(X, pd.DataFrame) else [f"X{i}" for i in range(X.shape[1])],
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False).head(10)

    fig = px.bar(importances_df, x="Importance", y="Feature", orientation="h", title="Top 10 Feature Importances")
    st.plotly_chart(fig, use_container_width=True)

def compute_correlation_matrix(df_target, df_softs):
    if not df_softs:
        st.warning("Select soft indicators.")
        return

    df_corr = df_target[["Reference Period", "Actual"]].rename(columns={"Actual": "Target"})
    for soft_df, name in zip(df_softs, [f"Soft_{i+1}" for i in range(len(df_softs))]):
        df_corr = df_corr.merge(soft_df[["Reference Period", "Actual"]].rename(columns={"Actual": name}),
                                on="Reference Period", how="inner")

    corr = df_corr.drop(columns="Reference Period").corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu", aspect="auto")
    fig.update_layout(height=800, width=1200, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
