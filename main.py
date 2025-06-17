# main.py

import streamlit as st
from modules.ui import configure_sidebar, display_tabs
from modules.data_loader import load_data

# --- Streamlit Config ---
st.set_page_config(layout="wide", page_title="Economic Dashboard", page_icon="📊")
st.title("📊 Economic Indicator Analysis Dashboard")

# --- Sidebar Inputs ---
config = configure_sidebar()

# --- Load Data ---
df_target, df_softs = load_data(config)

# --- UI Tabs ---
display_tabs(config, df_target, df_softs)
