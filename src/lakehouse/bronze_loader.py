
from pyspark.sql import SparkSession
from pathlib import Path

spark = SparkSession.builder.appName("BronzeLayer").getOrCreate()

BASE = Path(__file__).resolve().parents[2]

sipd = spark.read.option("header", True).csv(str(BASE/"data/bronze/sipd_dummy.csv"))
sentiment = spark.read.option("header", True).csv(str(BASE/"data/bronze/sentiment_dummy.csv"))

print("Bronze SIPD")
sipd.show()

print("Bronze Sentiment")
sentiment.show()

spark.stop()
