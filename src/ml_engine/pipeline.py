"""
pipeline.py
=============
Orchestrator utama — menjalankan semua step ML Engine secara berurutan.

Steps:
1. Load/Generate data
2. Feature Engineering
3. Benford's Law Analysis
4. Isolation Forest Detection
5. Z-Score Detection
6. Ensemble Scoring
7. Graph Construction
8. Entity Resolution
9. Community Detection
10. Graph Risk Scoring
11. Final Export ke Gold Layer
"""

import pandas as pd
import numpy as np
import time
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_engine.config import SILVER_DIR, ML_OUTPUT_DIR

# Data sources
from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data
from ml_engine.process_lpse_silver import process_lpse_data
from ingestion.ingest_ckan_apbd import run_ckan_ingestion
from ml_engine.process_ckan_silver import process_ckan_to_silver

# Anomaly detection
from ml_engine.anomaly_detection.benford_analysis import run_benford_analysis
from ml_engine.anomaly_detection.isolation_forest import engineer_features, run_isolation_forest
from ml_engine.anomaly_detection.zscore_detector import run_zscore_detection
from ml_engine.anomaly_detection.ensemble import run_ensemble

# Graph analysis
from ml_engine.graph_analysis.neo4j_loader import build_graph
from ml_engine.graph_analysis.entity_resolver import run_entity_resolution
from ml_engine.graph_analysis.community_detector import run_community_detection
from ml_engine.graph_analysis.risk_scorer import run_risk_scoring

# Export & Visualization
from ml_engine.export_gold import export_all_gold
from ml_engine.visualize import generate_all_visualizations


def run_pipeline(
    use_ckan: bool = True,
    use_synthetic: bool = True,
    generate_data: bool = True,
    save_intermediates: bool = True,
    generate_plots: bool = True,
) -> dict:
    """
    Jalankan full ML Engine pipeline.

    Parameters
    ----------
    use_ckan : bool
        Gunakan data asli dari API CKAN Surabaya (True) atau data sintetis (False).
    generate_data : bool
        Generate data baru (True) atau load existing (False).
    save_intermediates : bool
        Simpan hasil intermediate ke CSV.
    generate_plots : bool
        Generate visualisasi.

    Returns
    -------
    dict
        Dictionary berisi semua output (DataFrames, graph, dll).
    """
    start_time = time.time()

    print("╔" + "═" * 60 + "╗")
    print("║   SmartBudget ML Engine — Full Pipeline                   ║")
    print("║   Deteksi Anomali & Analisis Graf APBD                    ║")
    print("╚" + "═" * 60 + "╝")

    results = {}

    # ==============================================================
    # STEP 1: Data Loading / Generation
    # ==============================================================
    print("\n\n▶ STEP 1: Data Loading")
    print("-" * 40)

    if use_ckan:
        print("  Using real data from CKAN API...")
        if generate_data:
            run_ckan_ingestion()
        df_transactions = process_ckan_to_silver()
        _, df_vendors = process_lpse_data()
    elif use_synthetic and generate_data:
        df_transactions = generate_apbd_data(save=save_intermediates)
        _, df_vendors = process_lpse_data()
    elif use_synthetic:
        # Load from existing CSVs
        trx_path = SILVER_DIR / "silver_apbd_belanja.csv"
        vendor_path = SILVER_DIR / "silver_vendor_network.csv"

        if trx_path.exists() and vendor_path.exists():
            df_transactions = pd.read_csv(trx_path)
            df_vendors = pd.read_csv(vendor_path)
            print(f"  Loaded {len(df_transactions)} transactions from {trx_path}")
            print(f"  Loaded {len(df_vendors)} vendors from {vendor_path}")
        else:
            print("  Data not found, generating synthetic data/processing LPSE...")
            df_transactions = generate_apbd_data(save=save_intermediates)
            _, df_vendors = process_lpse_data()
    else:
        # Load real data from Silver layer
        df_transactions = pd.read_csv(SILVER_DIR / "silver_apbd_belanja.csv")
        _, df_vendors = process_lpse_data() # Process LPSE if real data used
        if df_vendors is None:
            df_vendors = pd.read_csv(SILVER_DIR / "silver_vendor_network.csv")

    results["df_transactions_raw"] = df_transactions.copy()
    results["df_vendors_raw"] = df_vendors.copy()

    # ==============================================================
    # STEP 2: Feature Engineering
    # ==============================================================
    print("\n\n▶ STEP 2: Feature Engineering")
    print("-" * 40)
    df_transactions = engineer_features(df_transactions)
    print(f"  Features added: {len(df_transactions.columns)} columns")

    # ==============================================================
    # STEP 3: Benford's Law Analysis
    # ==============================================================
    print("\n\n▶ STEP 3: Benford's Law Analysis")
    print("-" * 40)
    df_transactions, benford_skpd, benford_kota = run_benford_analysis(
        df_transactions, save=save_intermediates
    )
    results["benford_skpd"] = benford_skpd
    results["benford_kota"] = benford_kota

    # ==============================================================
    # STEP 4: Isolation Forest
    # ==============================================================
    print("\n\n▶ STEP 4: Isolation Forest")
    print("-" * 40)
    df_transactions = run_isolation_forest(df_transactions, save=save_intermediates)

    # ==============================================================
    # STEP 5: Z-Score & Statistical Detection
    # ==============================================================
    print("\n\n▶ STEP 5: Z-Score & Statistical Detection")
    print("-" * 40)
    df_transactions = run_zscore_detection(df_transactions, save=save_intermediates)

    # ==============================================================
    # STEP 6: Ensemble Risk Scoring
    # ==============================================================
    print("\n\n▶ STEP 6: Ensemble Risk Scoring")
    print("-" * 40)
    df_transactions = run_ensemble(df_transactions, save=save_intermediates)
    results["df_transactions"] = df_transactions

    # ==============================================================
    # STEP 7: Graph Construction
    # ==============================================================
    print("\n\n▶ STEP 7: Knowledge Graph Construction")
    print("-" * 40)
    G = build_graph(df_transactions, df_vendors)
    results["graph"] = G

    # ==============================================================
    # STEP 8: Entity Resolution
    # ==============================================================
    print("\n\n▶ STEP 8: Entity Resolution")
    print("-" * 40)
    df_vendors, entity_pairs = run_entity_resolution(df_vendors, save=save_intermediates)
    results["entity_pairs"] = entity_pairs

    # ==============================================================
    # STEP 9: Community Detection
    # ==============================================================
    print("\n\n▶ STEP 9: Community Detection")
    print("-" * 40)
    centrality_df, communities = run_community_detection(G, save=save_intermediates)
    results["centrality_df"] = centrality_df
    results["communities"] = communities

    # ==============================================================
    # STEP 10: Graph Risk Scoring
    # ==============================================================
    print("\n\n▶ STEP 10: Vendor Risk Scoring")
    print("-" * 40)
    df_vendors = run_risk_scoring(
        df_vendors, df_transactions, entity_pairs, centrality_df,
        save=save_intermediates
    )
    results["df_vendors"] = df_vendors

    # ==============================================================
    # STEP 11: Export to Gold Layer
    # ==============================================================
    print("\n\n▶ STEP 11: Export to Gold Layer")
    print("-" * 40)
    gold_tables = export_all_gold(df_transactions, df_vendors)
    results["gold_tables"] = gold_tables

    # ==============================================================
    # STEP 12: Visualization (optional)
    # ==============================================================
    if generate_plots:
        print("\n\n▶ STEP 12: Generating Visualizations")
        print("-" * 40)
        generate_all_visualizations(
            df_transactions, df_vendors,
            benford_skpd, G, centrality_df,
        )

    # ==============================================================
    # SUMMARY
    # ==============================================================
    elapsed = time.time() - start_time

    print("\n\n" + "╔" + "═" * 60 + "╗")
    print("║   PIPELINE COMPLETE                                      ║")
    print("╚" + "═" * 60 + "╝")
    print(f"\n  ⏱  Total time: {elapsed:.1f} seconds")
    print(f"  📊 Transactions analyzed : {len(df_transactions)}")
    print(f"  🏢 Vendors analyzed      : {len(df_vendors)}")
    print(f"  ⚠️  Transaction anomalies: {df_transactions['is_flagged'].sum()}")
    print(f"  🔴 High-risk vendors     : {(df_vendors['graph_risk_category'].isin(['HIGH', 'CRITICAL'])).sum()}")
    print(f"  📁 Output directory      : {ML_OUTPUT_DIR}")

    return results


if __name__ == "__main__":
    results = run_pipeline(
        use_ckan=True,
        generate_data=True,
        save_intermediates=True,
        generate_plots=True,
    )
