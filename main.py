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

# --- Footer ---
st.markdown("""
    <hr style="margin-top: 50px;">
    <div style='text-align: center; padding: 10px; font-size: 0.9em; color: grey;'>
        Made with ❤️ by Ankush Kumar<br>
        <span style='font-size: 0.8em;'>Indian Institute of Technology Kharagpur</span><br>
        <a href='https://github.com/ankushkgpian' target='_blank'>GitHub</a> &nbsp;|&nbsp;
        <a href='https://www.linkedin.com/in/ankushkgpian/' target='_blank'>LinkedIn</a>
    </div>
""", unsafe_allow_html=True)

# --- Custom Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif !important;
        }

        h1 {
            font-size: 2.2rem;
            font-weight: 700;
            color: #0B5394;
        }

        h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: #0B5394;
        }

        h3 {
            font-size: 1.5rem;
            font-weight: 600;
            color: #0B5394;
        }

        h4 {
            font-size: 1.2rem;
            font-weight: 600;
            color: #0B5394;
        }

        p, .stMarkdown, .stDataFrame, .stTable {
            font-size: 1rem;
        }

        .stButton>button {
            background-color: #0B5394;
            color: white;
            font-weight: 600;
            border-radius: 6px;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 15px;
            font-weight: 600;
            padding: 10px 24px;
            font-family: 'Montserrat', sans-serif !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .stSidebar, label, .stSelectbox, .stMultiSelect, .stSlider {
            font-size: 0.95rem;
        }
    </style>
""", unsafe_allow_html=True)
