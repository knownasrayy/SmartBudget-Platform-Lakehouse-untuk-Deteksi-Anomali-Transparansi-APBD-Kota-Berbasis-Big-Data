"""
run_pipeline.py — SmartBudget Lakehouse Pipeline
Entry point utama: Bronze → Silver → Join → Gold

Cara run:
    cd src/lakehouse
    python run_pipeline.py
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bronze_loader   import get_spark, run_bronze
from silver_transform import run_silver
from spark_join       import run_join
from gold_aggregation import run_gold
from pyspark.sql.functions import col


def run_pipeline():
    t_total = time.time()

    print("=" * 60)
    print("  SmartBudget Lakehouse Pipeline")
    print("  Bronze ─► Silver ─► Join ─► Gold")
    print("=" * 60)

    spark = get_spark()
    spark.sparkContext.setLogLevel("WARN")
    print("[Spark] Session ready\n")

    try:
        # Step 1: Bronze
        print("[Step 1] Bronze — Load CSV dari Adel...")
        t = time.time()
        run_bronze(spark)
        print(f"  ✓ {time.time()-t:.1f}s\n")

        # Step 2: Silver
        print("[Step 2] Silver — Cleaning & Transformasi...")
        t = time.time()
        run_silver(spark)
        print(f"  ✓ {time.time()-t:.1f}s\n")

        # Step 3: Join SIPD + Sentimen
        print("[Step 3] Join — SIPD ⋈ Sentimen Publik...")
        t = time.time()
        run_join(spark)
        print(f"  ✓ {time.time()-t:.1f}s\n")

        # Step 4: Gold
        print("[Step 4] Gold — Agregasi & Anomaly Flagging...")
        t = time.time()
        df_gold, df_summary = run_gold(spark)
        print(f"  ✓ {time.time()-t:.1f}s\n")

        print("=" * 60)
        print(f"  PIPELINE SELESAI — Total: {time.time()-t_total:.1f}s")
        print("=" * 60)

        print("\n>>> Distribusi Flag Anomali (Gold):")
        df_gold.groupBy("flag_anomali").count().orderBy("count", ascending=False).show()

        print(">>> Top 5 Transaksi Berisiko:")
        (
            df_gold
            .filter(col("flag_anomali") != "NORMAL")
            .select("id_transaksi","kota","nama_skpd","pagu_anggaran",
                    "persentase_realisasi","flag_anomali","risk_score")
            .orderBy(col("risk_score").desc())
            .show(5, truncate=False)
        )

        print(">>> Summary per SKPD (Top Anomali):")
        df_summary.orderBy(col("jumlah_anomali").desc()).show(8, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    run_pipeline()
