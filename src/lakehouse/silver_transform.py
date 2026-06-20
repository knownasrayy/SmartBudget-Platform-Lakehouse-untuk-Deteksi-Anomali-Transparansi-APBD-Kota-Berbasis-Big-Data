import os
import glob
from pathlib import Path
import pyspark
from pyspark.sql.functions import col
from pyspark.sql.types import LongType
from delta import *

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return max(files, key=os.path.getctime)

BASE = Path(__file__).resolve().parents[2]
os.environ["HADOOP_HOME"] = str(BASE / "hadoop")

# Configure Spark Session with Delta Lake support
builder = pyspark.sql.SparkSession.builder.appName("SmartBudget_Silver_Transform") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
# Reduce logging verbosity
spark.sparkContext.setLogLevel("WARN")

BASE = Path(__file__).resolve().parents[2]

bronze_pattern = str(BASE / "data/bronze/apbd_surabaya_raw_*.csv")
latest_bronze_file = get_latest_file(bronze_pattern)
print(f"Membaca file Bronze terbaru: {latest_bronze_file}")

# Read CSV with Spark
df = spark.read.csv(latest_bronze_file, header=True, inferSchema=True)

# 1. Drop NA and duplicates
df_clean = df.dropna(subset=["id", "anggaran", "realisasi"]).dropDuplicates()

# 2. Cast types and rename
df_silver = df_clean \
    .withColumn("pagu_anggaran", col("anggaran").cast(LongType())) \
    .withColumn("realisasi", col("realisasi").cast(LongType())) \
    .withColumnRenamed("skpd", "nama_skpd") \
    .drop("anggaran")

# 3. Add missing fallback columns if they don't exist
existing_cols = df_silver.columns

if "kode_skpd" not in existing_cols:
    df_silver = df_silver.withColumn("kode_skpd", col("nama_skpd"))
if "kode_rekening" not in existing_cols:
    df_silver = df_silver.withColumn("kode_rekening", col("kategori_belanja"))
if "tanggal_kontrak" not in existing_cols:
    df_silver = df_silver.withColumn("tanggal_kontrak", col("tanggal_input"))
if "id_vendor" not in existing_cols:
    df_silver = df_silver.withColumn("id_vendor", col("id"))
if "id_transaksi" not in existing_cols:
    df_silver = df_silver.withColumn("id_transaksi", col("id"))

out_dir = str(BASE / "data/silver/silver_apbd_belanja.delta")

# 4. Save to Delta Lake format
df_silver.write.format("delta").mode("overwrite").save(out_dir)

print(f"Silver layer berhasil dibuat di: {out_dir}")
df_silver.show(5)

spark.stop()
