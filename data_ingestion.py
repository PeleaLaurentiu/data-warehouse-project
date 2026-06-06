import requests
from datetime import datetime
from repository import db, TimeSeriesRepository 

API_Key = "Insert you api key here"

class DataIngestor:
    def __init__(self, vendor_name, asset_symbol):
        self.vendor = db["Vendors"].find_one({"vendor_name": vendor_name})
        self.asset = db["Assets"].find_one({"symbol": asset_symbol, "active": True})

    def fetch_and_store(self):
        raise NotImplementedError("This method must be overridden in the child class.")

class AlphaVantageIngestor(DataIngestor):
    def fetch_and_store(self):
        if not self.vendor or not self.asset:
            print("Missing MSFT Vendor or Asset in database.")
            return

        print("Starting data ingestion for MSFT...")
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey={API_Key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "Time Series (Daily)" in data:
                days = list(data["Time Series (Daily)"].items())[:100] 
                for day_str, vals in days:
                    ts = datetime.strptime(day_str, "%Y-%m-%d")
                    price_data = {
                        "open": float(vals["1. open"]), "close": float(vals["4. close"]),
                        "high": float(vals["2. high"]), "low": float(vals["3. low"]),
                        "volume": int(vals["5. volume"])
                    }
                    TimeSeriesRepository.insert_record(self.asset["_id"], self.vendor["_id"], ts, price_data)
                print("MSFT data ingestion completed successfully!")

class CoinGeckoIngestor(DataIngestor):
    def fetch_and_store(self):
        if not self.vendor or not self.asset:
            print("Missing BTC Vendor or Asset in database.")
            return

        print("Starting data ingestion for BTC...")
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=100&interval=daily"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            for i in range(len(prices)):
                ts = datetime.fromtimestamp(prices[i][0] / 1000)
                price_data = {
                    "price_usd": round(prices[i][1], 2),
                    "volume_24h": round(volumes[i][1], 2)
                }
                TimeSeriesRepository.insert_record(self.asset["_id"], self.vendor["_id"], ts, price_data)
            print("BTC data ingestion completed successfully!")

if __name__ == "__main__":
    msft_ingestor = AlphaVantageIngestor("Alpha Vantage", "MSFT")
    msft_ingestor.fetch_and_store()
    
    btc_ingestor = CoinGeckoIngestor("Coin Gecko", "BTC")
    btc_ingestor.fetch_and_store()