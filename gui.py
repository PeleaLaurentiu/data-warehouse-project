import streamlit as st
from google import genai
from google.genai import types
import requests

st.set_page_config(page_title="Financial Agentic AI")
st.title("Financial Agentic AI")
st.markdown("Ask me about assets, vendors or forecasts.")

API_Key = "insert you api key here"
client = genai.Client(api_key=API_Key)
base_url = "http://localhost:8000"

def get_assets():
    response = requests.get(f"{base_url}/assets")
    return response.text

def get_asset_statistics(asset_id: str):
    response = requests.get(f"{base_url}/analytics/summary", params={'asset_id': asset_id})
    return response.text

def get_asset_forecast(asset_id: str):
    response = requests.get(f"{base_url}/analytics/forecast", params={'asset_id': asset_id})
    return response.text

def get_vendors():
    response = requests.get(f"{base_url}/vendors")
    return response.text

#Initialize the chat session
if "chat_session" not in st.session_state:
   st.session_state.chat_session = client.chats.create(
    model="models/gemini-2.0-flash-lite",
    config=types.GenerateContentConfig(
        tools=[get_assets, get_asset_statistics, get_asset_forecast, get_vendors]
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#Text box logic
if prompt := st.chat_input("What is your question?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("The agent is thinking..."):
            try:
                response = st.session_state.chat_session.send_message(
                    f"You are a financial agent. Use the tools to answer the user request. Use the appropriate tool for this request: {prompt}"
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")