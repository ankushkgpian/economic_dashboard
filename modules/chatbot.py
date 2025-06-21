# modules/chatbot.py
import openai
import streamlit as st

openai.api_key = st.secrets["openai_api_key"]

def ask_chatbot(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
