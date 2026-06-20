import os
from pathlib import Path
import pyspark
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.functions import udf, col, percent_rank
from pyspark.sql.window import Window
from pyspark.sql.types import FloatType
from delta import *
import numpy as np
import glob
import shutil

BASE = Path(__file__).resolve().parents[2]
os.environ["HADOOP_HOME"] = str(BASE / "hadoop")

# Configure Spark Session with Delta Lake support
builder = pyspark.sql.SparkSession.builder.appName("SmartBudget_MLlib_Anomaly") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

BASE = Path(__file__).resolve().parents[2]
silver_file = str(BASE / "data/silver/silver_apbd_belanja.csv")

print(f"Membaca data dari Silver Layer APBD (Data Generative/Sintetis): {silver_file}")
try:
    df = spark.read.csv(silver_file, header=True, inferSchema=True)
except Exception as e:
    print(f"Error reading silver file: {e}")
    spark.stop()
    exit(1)

# --- FEATURE ENGINEERING ---
# Map APBD columns to expected Gold schema
import pyspark.sql.functions as F

df = df.withColumn("id", col("id_transaksi")) \
       .withColumn("tahun", col("tahun_anggaran")) \
       .withColumn("kategori_belanja", col("uraian_belanja")) \
       .withColumn("nama_skpd", col("nama_skpd")) \
       .withColumn("pagu_anggaran", col("pagu_anggaran")) \
       .withColumn("realisasi", col("realisasi")) \
       .withColumn("persen_realisasi", col("persen_realisasi")) \
       .withColumn("jenis_pengadaan", col("jenis_pengadaan")) \
       .withColumn("tanggal_input", col("tanggal_kontrak")) \
       .withColumn("nama_vendor", col("nama_vendor")) \
       .withColumn("id_vendor", col("id_vendor")) \
       .withColumn("kota", col("kota"))

df = df.dropna(subset=["pagu_anggaran", "realisasi"])

# We will detect anomalies based on 'pagu_anggaran' and 'realisasi'
assembler = VectorAssembler(inputCols=["pagu_anggaran", "realisasi"], outputCol="features_raw")
df_feat = assembler.transform(df)

scaler = StandardScaler(inputCol="features_raw", outputCol="features", withStd=True, withMean=True)
scaler_model = scaler.fit(df_feat)
df_scaled = scaler_model.transform(df_feat)

# --- MACHINE LEARNING (K-Means Clustering) ---
print("Melatih model K-Means clustering menggunakan Spark MLlib...")
kmeans = KMeans(k=5, seed=42, featuresCol="features", predictionCol="cluster")
model = kmeans.fit(df_scaled)

# Make predictions
predictions = model.transform(df_scaled)

# Calculate Silhouette Score just for logging
evaluator = ClusteringEvaluator(predictionCol="cluster")
silhouette = evaluator.evaluate(predictions)
print(f"Silhouette with squared euclidean distance = {silhouette}")

from pyspark.ml.functions import vector_to_array
import pyspark.sql.functions as F

# Compute distance using native PySpark SQL to avoid Python worker crashes
centers = model.clusterCenters()

scored_df = predictions.withColumn("features_arr", vector_to_array(col("features")))
scored_df = scored_df.withColumn("f1", col("features_arr")[0])
scored_df = scored_df.withColumn("f2", col("features_arr")[1])

dist_expr = F.lit(0.0)
for i, center in enumerate(centers):
    c1, c2 = float(center[0]), float(center[1])
    dist_sq = (col("f1") - c1)**2 + (col("f2") - c2)**2
    dist_expr = F.when(col("cluster") == i, F.sqrt(dist_sq)).otherwise(dist_expr)

scored_df = scored_df.withColumn("anomaly_score", dist_expr)

# Flag top 5% highest scores as anomalies
window = Window.orderBy("anomaly_score")
scored_df = scored_df.withColumn("rank", percent_rank().over(window))
final_df = scored_df.withColumn("is_anomaly", (col("rank") > 0.95).cast("int"))

# Select relevant columns for Gold
gold_anomaly = final_df.select(
    "id", "tahun", "nama_skpd", "kategori_belanja", 
    "pagu_anggaran", "realisasi", "persen_realisasi", "jenis_pengadaan",
    "tanggal_input", "nama_vendor", "id_vendor", "kota",
    "cluster", "anomaly_score", "is_anomaly"
)

out_dir_delta = str(BASE / "data/gold/gold_anomaly_transactions.delta")
out_dir_csv = str(BASE / "data/gold/gold_anomaly_transactions_csv")
out_file_final = str(BASE / "data/gold/gold_anomaly_transactions.csv")

# Save as Delta
print(f"Menyimpan hasil Anomaly Detection ke Delta Lake: {out_dir_delta}")
gold_anomaly.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(out_dir_delta)

# Save as CSV for Dashboard
gold_anomaly.coalesce(1).write.csv(out_dir_csv, header=True, mode="overwrite")
csv_parts = glob.glob(out_dir_csv + "/*.csv")
if csv_parts:
    shutil.copy(csv_parts[0], out_file_final)

# Generate gold_skpd_summary
print("Menyimpan SKPD summary...")
gold_skpd_summary = gold_anomaly.groupBy("nama_skpd") \
    .agg(
        F.sum("pagu_anggaran").alias("total_pagu"),
        F.sum("realisasi").alias("total_realisasi"),
        F.count("id").alias("jumlah_proyek")
    )
out_dir_skpd_csv = str(BASE / "data/gold/gold_skpd_summary_csv")
out_file_skpd_final = str(BASE / "data/gold/gold_skpd_summary.csv")
gold_skpd_summary.coalesce(1).write.csv(out_dir_skpd_csv, header=True, mode="overwrite")
csv_skpd_parts = glob.glob(out_dir_skpd_csv + "/*.csv")
if csv_skpd_parts:
    shutil.copy(csv_skpd_parts[0], out_file_skpd_final)

print("Selesai! Sample data anomali:")
gold_anomaly.filter(col("is_anomaly") == 1).show(5)

spark.stop()
