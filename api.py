from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from repository import AssetRepository, VendorRepository, TimeSeriesRepository
from spark import SparkAnalyticsWorkflow

main = FastAPI(title="Data Warehouse API", description="API created for Data Warehouse final project")

@main.get("/")
def home():
    return {"message": "Welcome to the Data Warehouse project API!"}

#Q1: Return limited info about all financial assets
@main.get("/assets")
def get_assets(skip: int = 0, limit: int = 100):
    assets = AssetRepository.get_all(skip=skip, limit=limit)
    result = [{"id": a["_id"], "symbol": a["symbol"]} for a in assets]
    return {"status": "success", "count": len(result), "data": result}

#Q2: Return all the details of an asset knowing its identifier
@main.get("/assets/{asset_id}")
def get_asset_details(asset_id: str):
    asset = AssetRepository.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"status": "success", "data": asset}
    
#Q3: Return limited info about all sources of data
@main.get("/vendors")
def get_vendors(skip: int = 0, limit: int = 100):
    vendors = VendorRepository.get_all(skip=skip, limit=limit)
    result = [{"id": v["_id"], "vendor_name": v["vendor_name"]} for v in vendors]
    return {"status": "success", "count": len(result), "data": result}

#Q4: Return all the details of a data source knowing its identifier
@main.get("/vendors/{vendors_id}")
def get_vendor_details(vendors_id: str):
    vendor = VendorRepository.get_by_id(vendors_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"status": "success", "data": vendor}
    
#Q5: Return timeseries data for specified asset and data source identifiers
@main.get("/timeseries")
def get_timeseries(
    asset_id: str, 
    vendor_id: Optional[str] = None, 
    from_date: Optional[str] = None, 
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    ts_data = TimeSeriesRepository.get_timeseries(
        asset_id=asset_id, 
        vendor_id=vendor_id,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )
    return {"status": "success", "count": len(ts_data), "data": ts_data}
    
#UC3: min, max, mean
@main.get("/analytics/summary")
def get_analytics_summary(asset_id: str):
    asset = AssetRepository.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found in the database")
    
    symbol = str(asset.get("symbol", "")).upper()
    
    try:
        stats = SparkAnalyticsWorkflow.run_aggregation_pipeline(asset_id, symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical Spark Error: {str(e)}")
    
    if not stats:
        raise HTTPException(status_code=404, detail=f"No time series data found for {symbol} to compute summary")

    return {
        "status": "success",
        "asset": symbol,
        "analytics": stats
    }

#UC3: forecast and trend
@main.get("/analytics/forecast")
def get_analytics_forecast(asset_id: str):
    asset = AssetRepository.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found in the database")
    
    symbol = str(asset.get("symbol", "")).upper()
    
    try:
        forecast = SparkAnalyticsWorkflow.run_ml_prediction_pipeline(asset_id, symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical Spark ML Error: {str(e)}")

    if not forecast:
        raise HTTPException(status_code=404, detail=f"At least 3 days of recent price data required to train the Spark ML model for {symbol}")

    return {
        "status": "success",
        "asset": symbol,
        "forecast": forecast
    }