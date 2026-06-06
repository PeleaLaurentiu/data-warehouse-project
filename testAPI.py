from fastapi.testclient import TestClient
from api import main

client = TestClient(main)

def test_home_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Data Warehouse project API!"}

def test_get_assets_route():
    response = client.get("/assets")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data

def test_get_vendors_route():
    response = client.get("/vendors")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "count" in data

def test_invalid_asset_details():
    response = client.get("/assets/12345invalidID")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid asset ID format"