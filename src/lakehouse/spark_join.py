
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pathlib import Path

spark = SparkSession.builder.appName("JoinLayer").getOrCreate()
BASE = Path(__file__).resolve().parents[2]

sipd = (
    spark.read.option("header",True)
    .csv(str(BASE/"data/bronze/sipd_dummy.csv"))
    .withColumn("anggaran", col("anggaran").cast("long"))
)

sent = spark.read.option("header",True).csv(str(BASE/"data/bronze/sentiment_dummy.csv"))

joined = sipd.join(sent, "id_proyek", "inner")

joined.write.mode("overwrite").option("header",True).csv(str(BASE/"data/silver/joined_data"))

joined.show()
spark.stop()
