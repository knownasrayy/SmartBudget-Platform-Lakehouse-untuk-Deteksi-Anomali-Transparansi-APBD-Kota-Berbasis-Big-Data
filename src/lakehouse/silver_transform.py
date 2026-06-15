"""
silver_transform.py — Silver Layer
Bronze CSV → cleaning via Spark → simpan via Pandas
"""

import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_date, trim, round as spark_round,
    row_number, lit, current_timestamp, when
)
from pyspark.sql.window import Window

BASE = Path(__file__).resolve().parents[2]


def get_spark():
    return (
        SparkSession.builder
        .appName("SmartBudget-Silver")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def run_silver(spark):
    in_path = str(BASE / "data" / "bronze_out" / "bronze_data.csv")
    out_dir = str(BASE / "data" / "silver_out")
    os.makedirs(out_dir, exist_ok=True)

    print("[Silver] Membaca Bronze CSV...")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(in_path.replace("\\", "/"))
    print(f"[Silver] Records masuk: {df.count()}")

    df = (
        df
        .withColumn("tanggal_scraping",    to_date(col("tanggal_scraping"), "yyyy-MM-dd"))
        .withColumn("pagu_anggaran",        col("pagu_anggaran").cast("double"))
        .withColumn("realisasi",            col("realisasi").cast("double"))
        .withColumn("persentase_realisasi", col("persentase_realisasi").cast("double"))
        .withColumn("tahun_anggaran",       col("tahun_anggaran").cast("integer"))
    )

    for c in ["kota", "nama_skpd", "kecamatan", "jenis_belanja", "status"]:
        df = df.withColumn(c, trim(col(c)))

    before = df.count()
    df = df.dropna(subset=["id_transaksi", "pagu_anggaran", "realisasi", "nama_skpd", "kota"])
    print(f"[Silver] Null drop: {before - df.count()} records")

    before2 = df.count()
    df = df.filter(col("pagu_anggaran") > 0)
    print(f"[Silver] Filter pagu <= 0: {before2 - df.count()} records")

    df = (
        df
        .withColumn("selisih",              spark_round(col("realisasi") - col("pagu_anggaran"), 2))
        .withColumn("persentase_realisasi", spark_round((col("realisasi") / col("pagu_anggaran")) * 100, 2))
        .withColumn("kategori_realisasi",
            when(col("persentase_realisasi") > 200, lit("EKSTREM"))
            .when(col("persentase_realisasi") > 130, lit("TINGGI"))
            .when(col("persentase_realisasi") >= 80,  lit("NORMAL"))
            .when(col("persentase_realisasi") >= 50,  lit("RENDAH"))
            .otherwise(lit("SANGAT_RENDAH"))
        )
        .withColumn("_layer",        lit("silver"))
        .withColumn("_processed_at", current_timestamp())
    )

    total = df.count()
    print(f"[Silver] Records final: {total}")

    out_path = os.path.join(out_dir, "silver_data.csv")
    df.toPandas().to_csv(out_path, index=False)
    print(f"[Silver] ✅ Disimpan → {out_path}")
    return df


if __name__ == "__main__":
    spark = get_spark()
    spark.sparkContext.setLogLevel("WARN")
    df = run_silver(spark)
    df.select("id_transaksi","kota","nama_skpd","pagu_anggaran","realisasi","persentase_realisasi","kategori_realisasi").show(10, truncate=False)
    spark.stop()
