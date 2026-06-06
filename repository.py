import pymongo
from bson import ObjectId
from datetime import datetime

CONNECTION_string = "mongodb+srv://laurentiupelea03:PASSWORDhere@cluster0.6wazjjo.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(CONNECTION_string)
db = client["DWproject"]

class AssetRepository:
    @staticmethod
    def get_all(skip: int = 0, limit: int = 100):
        assets = list(db["Assets"].find().skip(skip).limit(limit))
        for a in assets: 
            a["_id"] = str(a["_id"])
        return assets

    @staticmethod
    def get_by_id(asset_id: str):
        asset = db["Assets"].find_one({"_id": ObjectId(asset_id)})
        if asset: 
            asset["_id"] = str(asset["_id"])
        return asset

class VendorRepository:
    @staticmethod
    def get_all(skip: int = 0, limit: int = 100):
        vendors = list(db["Vendors"].find().skip(skip).limit(limit))
        for v in vendors: 
            v["_id"] = str(v["_id"])
        return vendors
        
    @staticmethod
    def get_by_id(vendor_id: str):
        vendor = db["Vendors"].find_one({"_id": ObjectId(vendor_id)})
        if vendor: 
            vendor["_id"] = str(vendor["_id"])
        return vendor

class TimeSeriesRepository:
    @staticmethod
    def get_timeseries(asset_id: str, vendor_id: str = None, from_date=None, to_date=None, skip: int = 0, limit: int = 100):
        query = {
            "asset_id": {"$in": [ObjectId(asset_id), asset_id]},
            "$or": [{"validTo": None}, {"validTo": {"$exists": False}}]
        }
        
        if vendor_id:
            query["vendor_id"] = {"$in": [ObjectId(vendor_id), vendor_id]}
            
        if from_date or to_date:
            query["timestamp"] = {}
            if from_date: 
                try:
                    dt = datetime.strptime(from_date, "%Y-%m-%d")
                    query["timestamp"]["$gte"] = dt
                except ValueError:
                    pass 
            if to_date: 
                try:
                    dt = datetime.strptime(to_date, "%Y-%m-%d")
                    query["timestamp"]["$lte"] = dt
                except ValueError:
                    pass
            
            if not query["timestamp"]:
                 del query["timestamp"]

        data = list(db["TimeSeriesData"].find(query).sort("timestamp", -1).skip(skip).limit(limit))
        
        for d in data:
            d["_id"] = str(d["_id"])
            d["asset_id"] = str(d["asset_id"])
            d["vendor_id"] = str(d["vendor_id"])
            
            if isinstance(d.get("timestamp"), datetime):
                d["timestamp"] = d["timestamp"].isoformat()
                
        return data
        
    @staticmethod
    def insert_record(asset_id, vendor_id, timestamp, price_data):
        now = datetime.now()
        
        existing = db["TimeSeriesData"].find_one({
            "asset_id": ObjectId(asset_id), 
            "timestamp": timestamp,
            "$or": [{"validTo": None}, {"validTo": {"$exists": False}}]
        })

        if existing and existing.get("priceData") == price_data:
            return

        #Expired marking for existing record if found
        if existing:
            db["TimeSeriesData"].update_one(
                {"_id": existing["_id"]},
                {"$set": {"validTo": now}}
            )

        #New record insertion
        new_record = {
            "asset_id": ObjectId(asset_id),
            "vendor_id": ObjectId(vendor_id),
            "timestamp": timestamp,
            "priceData": price_data,
            "validFrom": now,
            "validTo": None  
        }
        db["TimeSeriesData"].insert_one(new_record)