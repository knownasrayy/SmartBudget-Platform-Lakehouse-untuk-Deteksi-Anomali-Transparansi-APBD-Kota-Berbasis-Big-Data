
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pathlib import Path

spark = SparkSession.builder.appName("SilverLayer").getOrCreate()
BASE = Path(__file__).resolve().parents[2]

sipd = spark.read.option("header",True).csv(str(BASE/"data/bronze/sipd_dummy.csv"))

silver = (
    sipd.dropDuplicates()
        .dropna()
        .withColumn("anggaran", col("anggaran").cast("long"))
)

silver.write.mode("overwrite").option("header",True).csv(str(BASE/"data/silver/sipd_clean"))

print("Silver layer berhasil dibuat")
silver.show()

spark.stop()
