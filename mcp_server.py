from mcp.server.fastmcp import FastMCP
import requests
import json

mcp = FastMCP("FinancialDataWarehouse")

base_url = "http://localhost:8000"

def safe_api_call(endpoint: str, params: dict = None):
    try:
        response = requests.get(f"{base_url}/{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to API at {endpoint}. Details: {str(e)}"
    except Exception as e:
        return f"Error: Failed to process response. Details: {str(e)}"

@mcp.tool()
def get_assets() -> str:
    return safe_api_call("assets")

@mcp.tool()
def get_asset_statistics(asset_id: str) -> str:
    return safe_api_call("analytics/summary", params={'asset_id': asset_id})

@mcp.tool()
def get_asset_forecast(asset_id: str) -> str:
    return safe_api_call("analytics/forecast", params={'asset_id': asset_id})

@mcp.tool()
def get_vendors() -> str:
    return safe_api_call("vendors")

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()