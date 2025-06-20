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
    import os
    df_target = load_csv(os.path.join(config["folder"], config["target_file"]))
    
    # Load soft indicators using full relative paths (e.g., US/file.csv)
    df_softs = []
    for path in config["soft_files"]:
        folder, file = path.split("/")
        df_softs.append(load_csv(os.path.join(folder, file)))

    # Time filter
    start_year, end_year = config["year_range"]
    df_target = df_target[df_target["Reference Period"].dt.year.between(start_year, end_year)]
    for i in range(len(df_softs)):
        df_softs[i] = df_softs[i][df_softs[i]["Reference Period"].dt.year.between(start_year, end_year)]

    return df_target, df_softs



