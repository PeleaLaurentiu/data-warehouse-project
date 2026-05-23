import streamlit as st
from google import genai
from google.genai import types
import requests

#Page setup
st.set_page_config(page_title="Pelea Laurentiu - Financial AI Assistant")
st.title("Financial Data Assistant")
st.markdown("Ask me anything about assets, vendors, statistics or financial forecasts/statistics!")

#Config
API_Key = "AIzaSyAnhTseZejw2GjrFOhXvF8x4UHIlx9Buqc"
client = genai.Client(api_key=API_Key)
base_url = "http://localhost:8000"

def get_assets():
    """Fetches information about all financial assets from the API."""
    response = requests.get(f"{base_url}/assets")
    return response.json()

def get_asset_statistics(asset_id: str):
    """Fetches detailed information about a specific asset using its identifier."""
    response = requests.get(f"{base_url}/analytics/summary", params={'asset_id': asset_id})
    return response.json()

def get_asset_forecast(asset_id: str):
    """Fetches forecasted data for a specific asset using its identifier."""
    response = requests.get(f"{base_url}/analytics/forecast", params={'asset_id': asset_id})
    return response.json()

def get_vendors():
    """Fetches information about all data sources from the API."""
    response = requests.get(f"{base_url}/vendors")
    return response.json()

#Initialize the chat
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-flash-latest",
        config=types.GenerateContentConfig(
            tools=[get_assets, get_asset_statistics, get_asset_forecast, get_vendors]
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#Text box
if prompt := st.chat_input("What is your question?"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("The agent is thinking..."):
            try:
                response = st.session_state.chat_session.send_message(
                    f"You are a financial data assistant. Answer based on the provided information: {prompt}"
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Server error: {e}")