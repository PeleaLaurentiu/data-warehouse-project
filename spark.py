from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import min as spark_min, max as spark_max, avg as spark_avg, count as spark_count
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from repository import TimeSeriesRepository

spark = SparkSession.builder \
    .appName("DataWarehouseAnalytics") \
    .master("local[*]") \
    .getOrCreate()

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
                processed_data.append(Row(day_index=float(index), price=float(price)))

        if not processed_data:
            return None
            
        df = spark.createDataFrame(processed_data)
        return df

    @staticmethod
    def run_aggregation_pipeline(asset_id: str, symbol: str):
        df = SparkAnalyticsWorkflow._prepare_data(asset_id, symbol)
        if not df:
            return None

        agg_df = df.select(
            spark_count("price").alias("count"),
            spark_min("price").alias("min_price"),
            spark_max("price").alias("max_price"),
            spark_avg("price").alias("average_price")
        )
        
        result = agg_df.collect()[0]
        
        return {
            "count": int(result["count"]),
            "min_price": round(float(result["min_price"]), 2),
            "max_price": round(float(result["max_price"]), 2),
            "average_price": round(float(result["average_price"]), 2)
        }

    @staticmethod
    def run_ml_prediction_pipeline(asset_id: str, symbol: str):
        df = SparkAnalyticsWorkflow._prepare_data(asset_id, symbol)
        if not df or df.count() < 3:
            return None

        assembler = VectorAssembler(inputCols=["day_index"], outputCol="features")
        ml_df = assembler.transform(df)

        lr = LinearRegression(featuresCol="features", labelCol="price")
        lr_model = lr.fit(ml_df)
        
        next_day_index = float(df.count())
        next_day_df = spark.createDataFrame([Row(day_index=next_day_index)])
        next_day_ml_df = assembler.transform(next_day_df)
        
        prediction_df = lr_model.transform(next_day_ml_df)
        predicted_price = prediction_df.collect()[0]["prediction"]

        slope = lr_model.coefficients[0]
        trend = "Rising" if slope > 0 else "Falling"

        return {
            "method": "Apache Spark MLlib Linear Regression",
            "prediction_next_day_price": round(float(predicted_price), 2),
            "trend": trend
        }
