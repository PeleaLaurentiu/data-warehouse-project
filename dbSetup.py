import pymongo
from datetime import datetime

CONNECTION_string = "mongodb+srv://laurentiupelea03:(PASSWORD)@cluster0.6wazjjo.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(CONNECTION_string)
db = client["DWproject"]

#VENDORS
vendors = [{
    "vendor_name": "Alpha Vantage",
    "api_endpoint": "https://www.alphavantage.co/query",
},
{
    "vendor_name": "Coin Gecko",
    "api_endpoint": "https://api.coingecko.com/api/v3",
}]

vendor_insert = db["Vendors"].insert_many(vendors)
id_vendor = vendor_insert.inserted_ids

#ASSETS
assets = [{
    "symbol": "MSFT",
    "class": "stock",
    "description": "Microsoft Corporation",
    "region": "US",
    "validFrom": datetime.now(),
    "active": True,
},
{
    "symbol": "BTC",
    "class": "crypto",
    "description": "Bitcoin Cryptocurrency",
    "region": "global",
    "validFrom": datetime.now(),
    "active": True,
}]

asset_insert = db["Assets"].insert_many(assets)
id_asset = asset_insert.inserted_ids

for vendor, id_v in zip(vendors, id_vendor):
    print(f"Vendor '{vendor['vendor_name']}' with id: {id_v} has been inserted.")
print("\n")
for assets, id_a in zip(assets, id_asset):
    print(f"Asset '{assets['symbol']}' with id: {id_a} has been inserted.") 
