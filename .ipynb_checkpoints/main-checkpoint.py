# main.py

import streamlit as st
from modules.ui import configure_sidebar, display_tabs
from modules.data_loader import load_data

# --- Streamlit Config ---
st.set_page_config(layout="wide", page_title="Economic Dashboard", page_icon="📊")
st.title("Economic Indicator Analysis Dashboard")

# --- Sidebar Inputs ---
config = configure_sidebar()

# --- Load Data ---
df_target, df_softs = load_data(config)

# --- UI Tabs ---
display_tabs(config, df_target, df_softs)

st.markdown("""
    <hr style="margin-top: 50px;">
    <div style='text-align: center; padding: 10px; font-size: 0.9em; color: grey;'>
        Made with ❤️ by Ankush Kumar &nbsp;|&nbsp;
        <a href='https://github.com/ankushkgpian' target='_blank'>GitHub</a> &nbsp;|&nbsp;
        <a href='https://www.linkedin.com/in/ankushkgpian/' target='_blank'>LinkedIn</a>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    body {
        background-color: #F9F9F9;
        color: #333333;
    }
    .css-1d391kg, .css-ffhzg2 {
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #0B5394;
    }
    .stButton>button {
        background-color: #0B5394;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)
