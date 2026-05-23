import pymongo
import requests
from datetime import datetime

CONNECTION_string = "mongodb+srv://laurentiupelea03:(PASSWORD)@cluster0.6wazjjo.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(CONNECTION_string)
db = client["DWproject"]

API_Key = ""

#VENDOR
vendor_av = db["Vendors"].find_one({"vendor_name": "Alpha Vantage"})
vendor_cg = db["Vendors"].find_one({"vendor_name": "Coin Gecko"})

#ASSETS
asset_msft = db["Assets"].find_one({"symbol": "MSFT", "active": True})
asset_btc = db["Assets"].find_one({"symbol": "BTC", "active": True})

#Microsoft data ingestion

print("Starting data ingestion for MSFT...")

if vendor_av and asset_msft:
    url_msft = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey={API_Key}"
    answer_msft = requests.get(url_msft) 

    if answer_msft.status_code != 200:
        print("Error fetching data for MSFT: ", answer_msft.status_code)
    else:
        data_json_msft = answer_msft.json()

        if "Information" in data_json_msft or "Note" in data_json_msft:
            print("API limit reached: ", data_json_msft.get("Information", data_json_msft.get("Note")))
        elif "Time Series (Daily)" not in data_json_msft:
            print("Unexpected response format: ", data_json_msft)
        else: 
            days_data = data_json_msft["Time Series (Daily)"]
            days = list(days_data.items())

        if days:
            for day_str, daily_values in days:
                timestamp_obj = datetime.strptime(day_str, "%Y-%m-%d")
                
                existing_entry = db["TimeSeriesData"].find_one({
                    "asset_id": asset_msft["_id"],
                    "timestamp": timestamp_obj
                })
                
                if not existing_entry:
                    time_series_entry = {
                        "asset_id": asset_msft["_id"],
                        "vendor_id": vendor_av["_id"],
                        "timestamp": timestamp_obj,
                        "priceData": {
                            "open": float(daily_values["1. open"]),
                            "close": float(daily_values["4. close"]),
                            "high": float(daily_values["2. high"]),
                            "low": float(daily_values["3. low"]),
                            "volume": int(daily_values["5. volume"])
                        }
                    }
                    db["TimeSeriesData"].insert_one(time_series_entry)
                    print(f"Inserted MSFT data for {day_str}")
                else:
                    print(f"Skipped MSFT data for {day_str} (already exists).")
        else:
            print("No data found for MSFT.")

#Bitcoin data ingestion

print("\nStarting data ingestion for BTC...")

if vendor_cg and asset_btc:
    url_btc = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily"
    answer_btc = requests.get(url_btc)

    if answer_btc.status_code != 200:
        print("Error fetching data for BTC: ", answer_btc.status_code)
    else:
        data_json_btc = answer_btc.json()
        price_list = data_json_btc.get('prices')
        volume_list = data_json_btc.get('total_volumes')

    if price_list and volume_list:
        for i in range(len(price_list)):
            timestamp_ms = price_list[i][0]
            price_usd = round(price_list[i][1], 2)
            volume = round(volume_list[i][1], 2)

            timestamp_obj = datetime.fromtimestamp(timestamp_ms / 1000)

            existing_entry = db["TimeSeriesData"].find_one({
                "asset_id": asset_btc["_id"],
                "timestamp": timestamp_obj
            })

            if not existing_entry:
                time_series_entry = {
                    "asset_id": asset_btc["_id"],
                    "vendor_id": vendor_cg["_id"],
                    "timestamp": timestamp_obj,
                    "priceData": {
                        "price_usd": price_usd,
                        "volume_24h": volume
                    }
                }
                db["TimeSeriesData"].insert_one(time_series_entry)
                print(f"Inserted BTC data for timestamp {timestamp_obj.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"Skipped BTC data for {timestamp_obj.strftime('%Y-%m-%d %H:%M')} (already exists).")
    else:
        print("No data found for BTC.")
        
print("\nData ingestion completed!")

