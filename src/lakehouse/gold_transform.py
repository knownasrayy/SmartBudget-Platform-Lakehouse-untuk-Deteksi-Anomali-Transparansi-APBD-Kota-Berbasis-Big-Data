import os
from pathlib import Path
import pyspark
from pyspark.sql.functions import sum, count
from delta import *
import glob
import shutil

BASE = Path(__file__).resolve().parents[2]
os.environ["HADOOP_HOME"] = str(BASE / "hadoop")

# Configure Spark Session with Delta Lake support
builder = pyspark.sql.SparkSession.builder.appName("SmartBudget_Gold_Transform") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

BASE = Path(__file__).resolve().parents[2]
silver_dir = str(BASE / "data/silver/silver_apbd_belanja.delta")

print(f"Membaca data dari Silver Layer (Delta): {silver_dir}")

# Read Delta table
try:
    silver_df = spark.read.format("delta").load(silver_dir)
except Exception as e:
    print(f"Error reading silver delta table: {e}")
    spark.stop()
    exit(1)

# Aggregation for SKPD Summary
gold_skpd = silver_df.groupBy("nama_skpd").agg(
    sum("pagu_anggaran").alias("total_pagu"),
    sum("realisasi").alias("total_realisasi"),
    count("id").alias("jumlah_proyek")
)

out_dir_delta = str(BASE / "data/gold/gold_skpd_summary.delta")
out_dir_csv = str(BASE / "data/gold/gold_skpd_summary_csv")
out_file_final = str(BASE / "data/gold/gold_skpd_summary.csv")

# Save as Delta for Big Data standard
gold_skpd.write.format("delta").mode("overwrite").save(out_dir_delta)

# Save as CSV for Dashboard compatibility
gold_skpd.coalesce(1).write.csv(out_dir_csv, header=True, mode="overwrite")

# Rename the part file to actual csv filename
csv_parts = glob.glob(out_dir_csv + "/*.csv")
if csv_parts:
    shutil.copy(csv_parts[0], out_file_final)

print(f"Gold layer berhasil dibuat di: {out_dir_delta} (Delta) & {out_file_final} (CSV)")
gold_skpd.show(5)

spark.stop()
