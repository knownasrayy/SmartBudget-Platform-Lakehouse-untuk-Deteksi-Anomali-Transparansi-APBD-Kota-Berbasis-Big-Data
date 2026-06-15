"""
gold_aggregation.py — Gold Layer
Silver Joined CSV → Anomaly Flagging → simpan via Pandas
"""

import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, avg, count, round as spark_round,
    when, lit, current_timestamp, stddev
)
from pyspark.sql.window import Window

BASE = Path(__file__).resolve().parents[2]


def get_spark():
    return (
        SparkSession.builder
        .appName("SmartBudget-Gold")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def flag_anomali(df):
    w = Window.partitionBy("nama_skpd")
    df = (
        df
        .withColumn("_avg_skpd", avg("pagu_anggaran").over(w))
        .withColumn("_std_skpd", stddev("pagu_anggaran").over(w))
        .withColumn("_zscore", (col("pagu_anggaran") - col("_avg_skpd")) / (col("_std_skpd") + lit(1.0)))
    )
    df = (
        df
        .withColumn("flag_anomali",
            when(col("persentase_realisasi") > 200, lit("EKSTREM_OVER_BUDGET"))
            .when(col("persentase_realisasi") > 130, lit("OVER_BUDGET"))
            .when((col("jenis_belanja") == "Belanja Perjalanan Dinas") & (col("pagu_anggaran") > 5e10), lit("PERJALANAN_MENCURIGAKAN"))
            .when(col("_zscore") > 3.0, lit("OUTLIER_STATISTIK"))
            .when(col("avg_sentiment").isNotNull() & (col("avg_sentiment") < -0.3) & (col("persentase_realisasi") > 110), lit("KORELASI_SENTIMEN_NEGATIF"))
            .otherwise(lit("NORMAL"))
        )
        .withColumn("risk_score",
            when(col("flag_anomali") == "EKSTREM_OVER_BUDGET",        lit(10))
            .when(col("flag_anomali") == "PERJALANAN_MENCURIGAKAN",   lit(8))
            .when(col("flag_anomali") == "OVER_BUDGET",               lit(7))
            .when(col("flag_anomali") == "OUTLIER_STATISTIK",         lit(6))
            .when(col("flag_anomali") == "KORELASI_SENTIMEN_NEGATIF", lit(5))
            .otherwise(lit(1))
        )
        .drop("_avg_skpd", "_std_skpd")
    )
    return df


def run_gold(spark):
    in_path     = str(BASE / "data" / "silver_joined_out" / "silver_joined_data.csv")
    out_dir     = str(BASE / "data" / "gold_out")
    summary_dir = str(BASE / "data" / "gold_summary_out")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)

    print("[Gold] Membaca Silver Joined CSV...")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(in_path.replace("\\", "/"))
    print(f"[Gold] Records masuk: {df.count()}")

    df_flagged = flag_anomali(df)
    n_anomali = df_flagged.filter(col("flag_anomali") != "NORMAL").count()
    print(f"[Gold] Anomali terdeteksi: {n_anomali}")

    # Record-level
    out_path = os.path.join(out_dir, "gold_data.csv")
    df_flagged.toPandas().to_csv(out_path, index=False)
    print(f"[Gold] ✅ Record-level → {out_path}")

    # Summary
    df_summary = (
        df_flagged.groupBy("kota", "nama_skpd", "jenis_belanja", "tahun_anggaran")
        .agg(
            spark_round(spark_sum("pagu_anggaran"), 2).alias("total_pagu"),
            spark_round(spark_sum("realisasi"), 2).alias("total_realisasi"),
            spark_round(avg("persentase_realisasi"), 2).alias("avg_persen_realisasi"),
            count("*").alias("jumlah_transaksi"),
            spark_round(avg("avg_sentiment"), 3).alias("avg_sentiment"),
            spark_sum(when(col("flag_anomali") != "NORMAL", lit(1)).otherwise(lit(0))).alias("jumlah_anomali"),
            spark_round(spark_sum(when(col("flag_anomali") != "NORMAL", col("pagu_anggaran")).otherwise(lit(0.0))), 2).alias("nilai_anomali"),
        )
        .withColumn("_layer", lit("gold"))
        .withColumn("_created_at", current_timestamp())
    )

    summary_path = os.path.join(summary_dir, "gold_summary.csv")
    df_summary.toPandas().to_csv(summary_path, index=False)
    print(f"[Gold] ✅ Summary → {summary_path}")

    return df_flagged, df_summary


if __name__ == "__main__":
    spark = get_spark()
    spark.sparkContext.setLogLevel("WARN")
    df_gold, df_summary = run_gold(spark)
    print("\n=== Distribusi Flag Anomali ===")
    df_gold.groupBy("flag_anomali").count().orderBy("count", ascending=False).show()
    print("\n=== Top 10 Transaksi Berisiko ===")
    df_gold.filter(col("flag_anomali") != "NORMAL").select("id_transaksi","kota","nama_skpd","pagu_anggaran","persentase_realisasi","flag_anomali","risk_score").orderBy(col("risk_score").desc()).show(10, truncate=False)
    print("\n=== Summary per SKPD ===")
    df_summary.orderBy(col("jumlah_anomali").desc()).show(10, truncate=False)
    spark.stop()
