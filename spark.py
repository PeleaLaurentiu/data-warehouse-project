import numpy as np
from repository import TimeSeriesRepository

class SparkAnalyticsWorkflow:
    
    @staticmethod
    def _prepare_data(asset_id: str, symbol: str):
        raw_data = TimeSeriesRepository.get_timeseries(asset_id=asset_id)
        if not raw_data:
            return None

        processed_data = []
        raw_data.sort(key=lambda x: x["timestamp"]) 
        
        for index, item in enumerate(raw_data):
            price = None
            if symbol == "MSFT" and "close" in item["priceData"]:
                price = item["priceData"]["close"]
            elif symbol == "BTC" and "price_usd" in item["priceData"]:
                price = item["priceData"]["price_usd"]
            
            if price is not None:
                processed_data.append({
                    "day_index": float(index),
                    "price": float(price)
                })

        if not processed_data:
            return None
            
        return processed_data

    @staticmethod
    def run_aggregation_pipeline(asset_id: str, symbol: str):
        data = SparkAnalyticsWorkflow._prepare_data(asset_id, symbol)
        if not data:
            return None

        prices = [item["price"] for item in data]
        
        return {
            "count": len(prices),
            "min_price": round(min(prices), 2),
            "max_price": round(max(prices), 2),
            "average_price": round(sum(prices) / len(prices), 2)
        }

    @staticmethod
    def run_ml_prediction_pipeline(asset_id: str, symbol: str):
        data = SparkAnalyticsWorkflow._prepare_data(asset_id, symbol)
        if not data or len(data) < 3:
            return None

        x_vals = np.array([item["day_index"] for item in data])
        y_vals = np.array([item["price"] for item in data])

        coefficients = np.polyfit(x_vals, y_vals, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        next_day_index = float(len(data))
        predicted_price = (slope * next_day_index) + intercept

        trend = "Rising" if slope > 0 else "Falling"

        return {
            "method": "Linear Regression (Fallback Engine)",
            "prediction_next_day_price": round(predicted_price, 2),
            "trend": trend
        }