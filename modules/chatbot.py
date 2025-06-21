import openai
import streamlit as st

def ask_chatbot(prompt):
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        return "Missing OpenAI API key."

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
