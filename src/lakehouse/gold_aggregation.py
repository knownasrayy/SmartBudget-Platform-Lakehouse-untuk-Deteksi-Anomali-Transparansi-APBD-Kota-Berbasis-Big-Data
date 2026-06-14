
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, avg, count, col
from pathlib import Path

spark = SparkSession.builder.appName("GoldLayer").getOrCreate()
BASE = Path(__file__).resolve().parents[2]

sipd = (
    spark.read.option("header",True)
    .csv(str(BASE/"data/bronze/sipd_dummy.csv"))
    .withColumn("anggaran", col("anggaran").cast("long"))
)

sent = spark.read.option("header",True).csv(str(BASE/"data/bronze/sentiment_dummy.csv"))

joined = sipd.join(sent,"id_proyek")

gold = (
    joined.groupBy("dinas")
    .agg(
        sum("anggaran").alias("total_anggaran"),
        avg(col("sentiment_score").cast("double")).alias("avg_sentiment"),
        count("*").alias("jumlah_proyek")
    )
)

gold.write.mode("overwrite").option("header",True).csv(str(BASE/"data/gold/dashboard_ready"))

gold.show()
spark.stop()
