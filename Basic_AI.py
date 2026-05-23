from google import genai
from google.genai import types
import requests

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

chat = client.chats.create(
    model="gemini-flash-latest",
    config = types.GenerateContentConfig(
        tools = [get_assets, get_asset_statistics, get_asset_forecast, get_vendors]
    )
)

print("The chat bot is on!")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chat bot.")
        break
    
    print("Chat bot is thinking...")

    response = chat.send_message(
        f"You are a financial data assistant. Answer based on the provided information: {user_input}"
    )

    print(f"\nChat bot: {response.text}")
