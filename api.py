from fastapi import FastAPI, HTTPException
from bson.objectid import ObjectId
import pymongo
import statistics

main = FastAPI(title="Data Warehouse API", description="API created by Pelea Laurentiu for Data Warehouse final project")

CONNECTION_string = "mongodb+srv://laurentiupelea03:(password)@cluster0.6wazjjo.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(CONNECTION_string)
db = client["DWproject"]

@main.get("/")
def home():
    return {"message": "Welcome to the Data Warehouse project API!"}

#Q1 Return limited info about all financial assets
@main.get("/assets")
def get_assets():
    asset = db["Assets"].find({})
    result = [{"id": str(a["_id"]), "symbol": a["symbol"]} for a in asset]
    return {"status": "success", "count": len(result), "data": result}

#Q2 Return all the details of an asset knowing its identifier
@main.get("/assets/{asset_id}")
def get_asset_details(asset_id: str):
    try:
        asset = db["Assets"].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        asset["_id"] = str(asset["_id"])
        return {"status": "success", "data": asset}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset ID")
    
#Q3 Return limited info about all sources of data
@main.get("/vendors")
def get_vendors():
    vendors = db["Vendors"].find({})
    result = [{"id": str(v["_id"]), "vendor_name": v["vendor_name"]} for v in vendors]
    return {"status": "success", "count": len(result), "data": result}

#Q4 Return all the details of a data source knowing its identifier
@main.get("/vendors/{vendors_id}")
def get_vendor_details(vendors_id: str):
    try:
        vendor = db["Vendors"].find_one({"_id": ObjectId(vendors_id)})
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        vendor["_id"] = str(vendor["_id"])
        return {"status": "success", "data": vendor}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid vendor ID")
    
#Q5 Return timeseries data for specified asset and data source identifiers
@main.get("/timeseries")
def get_timeseries(asset_id: str, vendor_id: str):
    try:
        querry= {
            "asset_id": ObjectId(asset_id),
            "vendor_id": ObjectId(vendor_id)
        }
        ts_data = list(db["TimeSeriesData"].find(querry))

        for ts in ts_data:
            ts["_id"] = str(ts["_id"])
            ts["asset_id"] = str(ts["asset_id"])
            ts["vendor_id"] = str(ts["vendor_id"])

        return {"status": "success", "count": len(ts_data), "data": ts_data}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset or vendor ID")
    
#UC3 min, max, mean
@main.get("/analytics/summary")
def get_analysctics_summary(asset_id: str):
    try:
        asset = db["Assets"].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        ts_data = list(db["TimeSeriesData"].find({"asset_id": ObjectId(asset_id)}))
        if not ts_data:
            raise HTTPException(status_code=404, detail="No time series data found for this asset")
        
        prices = []
        for ts in ts_data:
            if asset["symbol"] == "MSFT" and "close" in ts["priceData"]:
                prices.append(ts["priceData"]["close"])
            elif asset["symbol"] == "BTC" and "price_usd" in ts["priceData"]:
                prices.append(ts["priceData"]["price_usd"])

        return {
            "status": "success",
            "asset": asset["symbol"],
            "analytics": {
                "count": len(prices),
                "min_price": min(prices),
                "max_price": max(prices),
                "average_price": round(statistics.mean(prices), 2)
            }
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset ID or no price data available")
    
#UC3 forecast and trend
@main.get("/analytics/forecast")
def get_analytics_forecast(asset_id: str):
    try:
        asset = db["Assets"].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        ts_data = list(db["TimeSeriesData"].find({"asset_id": ObjectId(asset_id)}).sort("timestamp", -1).limit(3))
        
        recent_prices = []
        for ts in ts_data:
            if asset["symbol"] == "MSFT":
                recent_prices.append(ts["priceData"]["close"])
            elif asset["symbol"] == "BTC":
                recent_prices.append(ts["priceData"]["price_usd"])

        if len(recent_prices) < 3:
            return {"status": "error", "message": "At least 3 days of recent price data to determine trend and forecast"}

        forecast_price = round(statistics.mean(recent_prices), 2)
        trend = "Rising " if recent_prices[0] >= recent_prices[1] else "Falling"

        return {
            "status": "success",
            "asset": asset["symbol"],
            "forecast": {
                "method": "3 days moving average",
                "prediction_next_day_price": forecast_price,
                "trend": trend,
                "recent_prices": recent_prices
            }
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid asset ID or insufficient price data")
