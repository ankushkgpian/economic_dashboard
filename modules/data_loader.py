# modules/data_loader.py

import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_csv(filepath):
    df = pd.read_csv(filepath, parse_dates=["Reference Period", "Release Date"])
    df["Surprise"] = df["Actual"] - df["Median_Forecast"]
    return df

def load_data(config):
    # Load target indicator
    target_path = os.path.join(".", config["target_country"], config["target_file"])
    df_target = load_csv(target_path)

    # Load soft indicators
    df_softs = []
    for src in config["soft_sources"]:
        file_path = os.path.join(".", src["country"], src["file"])
        df = load_csv(file_path)
        df["Source"] = f'{src["country"]}/{src["file"].replace(".csv", "")}'
        df_softs.append(df)

    # Apply year range filter
    start_year, end_year = config["year_range"]
    df_target = df_target[df_target["Reference Period"].dt.year.between(start_year, end_year)]
    for i in range(len(df_softs)):
        df_softs[i] = df_softs[i][df_softs[i]["Reference Period"].dt.year.between(start_year, end_year)]

    return df_target, df_softs


