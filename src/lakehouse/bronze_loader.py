"""
bronze_loader.py — Bronze Layer
Baca CSV dari data/bronze/raw/ → proses dengan Spark → simpan via Pandas (Windows compatible)
"""

import os
import glob
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType
)

BASE = Path(__file__).resolve().parents[2]

BRONZE_SCHEMA = StructType([
    StructField("id_transaksi",         StringType(),  True),
    StructField("tanggal_scraping",     StringType(),  True),
    StructField("kota",                 StringType(),  True),
    StructField("nama_skpd",            StringType(),  True),
    StructField("kecamatan",            StringType(),  True),
    StructField("jenis_belanja",        StringType(),  True),
    StructField("nama_kegiatan",        StringType(),  True),
    StructField("pagu_anggaran",        DoubleType(),  True),
    StructField("realisasi",            DoubleType(),  True),
    StructField("selisih",              DoubleType(),  True),
    StructField("persentase_realisasi", DoubleType(),  True),
    StructField("tahun_anggaran",       IntegerType(), True),
    StructField("sumber_data",          StringType(),  True),
    StructField("status",               StringType(),  True),
])


def get_spark():
    return (
        SparkSession.builder
        .appName("SmartBudget-Bronze")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def run_bronze(spark):
    raw_dir = str(BASE / "data" / "bronze" / "raw")
    out_dir = str(BASE / "data" / "bronze_out")
    os.makedirs(out_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"[Bronze] Tidak ada CSV di {raw_dir}")

    print(f"[Bronze] Ditemukan {len(csv_files)} file:")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")

    dfs = []
    for f in csv_files:
        df_tmp = (
            spark.read
            .schema(BRONZE_SCHEMA)
            .option("header", "true")
            .csv(f.replace("\\", "/"))
            .withColumn("_source_file", lit(os.path.basename(f)))
            .withColumn("_ingested_at", current_timestamp())
            .withColumn("_layer", lit("bronze"))
        )
        dfs.append(df_tmp)

    df = dfs[0]
    for d in dfs[1:]:
        df = df.union(d)

    total = df.count()
    print(f"[Bronze] Total records: {total}")

    # Simpan via pandas (bypass Hadoop NativeIO Windows)
    out_path = os.path.join(out_dir, "bronze_data.csv")
    df.toPandas().to_csv(out_path, index=False)
    print(f"[Bronze] ✅ Disimpan → {out_path}")
    return df


if __name__ == "__main__":
    spark = get_spark()
    spark.sparkContext.setLogLevel("WARN")
    df = run_bronze(spark)
    df.select("id_transaksi","kota","nama_skpd","pagu_anggaran","realisasi","status").show(5, truncate=False)
    spark.stop()
