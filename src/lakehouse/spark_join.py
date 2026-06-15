"""
spark_join.py — Join SIPD + Sentimen Publik
Silver CSV ⋈ tweets_berita_raw.csv → simpan via Pandas
Sentiment scoring pakai Spark native functions (no Python UDF)
"""

import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lower, trim, lit, current_timestamp,
    when, to_date, month, year, count as spark_count, avg,
    greatest, least
)

BASE = Path(__file__).resolve().parents[2]
KOTA_LIST = ["surabaya", "malang", "sidoarjo", "gresik", "mojokerto"]
NEGATIF = ["bocor", "korupsi", "janggal", "diabaikan", "terlambat", "fiktif", "markup"]
POSITIF = ["lancar", "baik", "meningkat", "berhasil", "diperbaiki"]


def get_spark():
    return (
        SparkSession.builder
        .appName("SmartBudget-Join")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def run_join(spark):
    silver_path = str(BASE / "data" / "silver_out" / "silver_data.csv")
    tweets_path = str(BASE / "data" / "bronze" / "tweets_berita_raw.csv")
    out_dir     = str(BASE / "data" / "silver_joined_out")
    os.makedirs(out_dir, exist_ok=True)

    print("[Join] Membaca Silver CSV...")
    df_apbd = spark.read.option("header", "true").option("inferSchema", "true").csv(silver_path.replace("\\", "/"))
    print(f"[Join] APBD records: {df_apbd.count()}")

    print("[Join] Membaca tweets_berita_raw.csv...")
    df_tweets = (
        spark.read
        .option("header", "true")
        .option("multiLine", "true")
        .option("escape", '"')
        .csv(tweets_path.replace("\\", "/"))
        .withColumn("tanggal", to_date(col("tanggal"), "yyyy-MM-dd"))
        .withColumn("teks_lower", lower(trim(col("teks"))))
    )

    # Ekstrak kota dari teks (native Spark)
    kota_expr = lit(None).cast("string")
    for kota in KOTA_LIST:
        kota_expr = when(col("teks_lower").contains(kota), lit(kota.capitalize())).otherwise(kota_expr)
    df_tweets = df_tweets.withColumn("kota_mention", kota_expr).filter(col("kota_mention").isNotNull())
    print(f"[Join] Tweets dengan mention kota: {df_tweets.count()}")

    # Sentiment scoring pakai Spark native (no UDF)
    neg_expr = lit(0)
    for w in NEGATIF:
        neg_expr = neg_expr + when(col("teks_lower").contains(w), lit(1)).otherwise(lit(0))

    pos_expr = lit(0)
    for w in POSITIF:
        pos_expr = pos_expr + when(col("teks_lower").contains(w), lit(1)).otherwise(lit(0))

    df_tweets = (
        df_tweets
        .withColumn("_neg", neg_expr)
        .withColumn("_pos", pos_expr)
        .withColumn("_total", col("_neg") + col("_pos"))
        .withColumn("sentiment_score",
            when(col("_total") == 0, lit(0.0))
            .otherwise((col("_pos") - col("_neg")).cast("double") / col("_total").cast("double"))
        )
        .drop("_neg", "_pos", "_total")
    )

    df_sentiment_agg = (
        df_tweets
        .withColumn("bulan", month(col("tanggal")))
        .withColumn("tahun", year(col("tanggal")))
        .groupBy("kota_mention", "tahun", "bulan")
        .agg(
            avg("sentiment_score").alias("avg_sentiment"),
            spark_count("*").alias("jumlah_tweet")
        )
        .withColumnRenamed("kota_mention", "kota")
    )

    df_joined = (
        df_apbd
        .join(df_sentiment_agg, on="kota", how="left")
        .withColumn("_layer", lit("silver_joined"))
        .withColumn("_joined_at", current_timestamp())
    )

    total = df_joined.count()
    print(f"[Join] Records setelah join: {total}")

    out_path = os.path.join(out_dir, "silver_joined_data.csv")
    df_joined.toPandas().to_csv(out_path, index=False)
    print(f"[Join] ✅ Disimpan → {out_path}")
    return df_joined


if __name__ == "__main__":
    spark = get_spark()
    spark.sparkContext.setLogLevel("WARN")
    df = run_join(spark)
    df.select("id_transaksi","kota","nama_skpd","pagu_anggaran","persentase_realisasi","avg_sentiment","jumlah_tweet").show(10, truncate=False)
    spark.stop()
