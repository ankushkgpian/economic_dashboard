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
    # Load target
    target_path = os.path.join(".", config["target_country"], config["target_file"])
    df_target = pd.read_csv(target_path, parse_dates=["Reference Period", "Release Date"])
    df_target["Surprise"] = df_target["Actual"] - df_target["Median_Forecast"]
    
    # Load soft indicators
    df_softs = []
    for entry in config["soft_indicators"]:
        path = os.path.join(".", entry["country"], entry["file"])
        df = pd.read_csv(path, parse_dates=["Reference Period", "Release Date"])
        df["Name"] = f"{entry['country']}_{entry['file'].replace('.csv', '')}"  # Labeling for clarity
        df_softs.append(df)

    return df_target, df_softs

