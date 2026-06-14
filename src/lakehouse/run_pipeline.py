from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count
from pathlib import Path

# =====================================================
# SPARK SESSION
# =====================================================

spark = (
    SparkSession.builder
    .appName("SmartBudgetPipeline")
    .master("local[*]")
    .getOrCreate()
)

# =====================================================
# PATH
# =====================================================

BASE = Path(__file__).resolve().parents[2]

SIPD_PATH = BASE / "data" / "bronze" / "sipd_dummy.csv"
SENTIMENT_PATH = BASE / "data" / "bronze" / "sentiment_dummy.csv"

# =====================================================
# BRONZE LAYER
# =====================================================

print("\n=== BRONZE LAYER ===")

sipd_bronze = (
    spark.read
    .option("header", True)
    .csv(str(SIPD_PATH))
)

sentiment_bronze = (
    spark.read
    .option("header", True)
    .csv(str(SENTIMENT_PATH))
)

print("Data SIPD:")
sipd_bronze.show(truncate=False)

print("Data Sentiment:")
sentiment_bronze.show(truncate=False)

# =====================================================
# SILVER LAYER
# =====================================================

print("\n=== SILVER LAYER ===")

sipd_silver = (
    sipd_bronze
    .dropDuplicates()
    .dropna()
    .withColumn("anggaran", col("anggaran").cast("long"))
)

print("Data SIPD Clean:")
sipd_silver.show(truncate=False)

# =====================================================
# JOIN SIPD + SENTIMENT
# =====================================================

print("\n=== JOIN DATA ===")

joined_df = (
    sipd_silver
    .join(sentiment_bronze, on="id_proyek", how="inner")
)

joined_df.show(truncate=False)

# =====================================================
# GOLD LAYER
# =====================================================

print("\n=== GOLD LAYER ===")

gold_df = (
    joined_df
    .groupBy("dinas")
    .agg(
        sum("anggaran").alias("total_anggaran"),
        avg(col("sentiment_score").cast("double")).alias("avg_sentiment"),
        count("*").alias("jumlah_proyek")
    )
)

gold_df.show(truncate=False)

print("\nPIPELINE BERHASIL DIJALANKAN")

spark.stop()