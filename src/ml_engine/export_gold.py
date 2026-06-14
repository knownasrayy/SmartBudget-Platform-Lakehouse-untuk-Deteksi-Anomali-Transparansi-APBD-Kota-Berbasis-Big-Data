"""
export_gold.py
================
Export hasil analisis ke Gold Layer (tabel siap konsumsi dashboard).

Output:
1. gold_anomaly_transactions.csv — Semua transaksi + flag & risk score
2. gold_vendor_risk_profile.csv — Profil risiko per vendor
3. gold_skpd_summary.csv — Ringkasan anomali per SKPD per kota
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_engine.config import GOLD_DIR


def export_anomaly_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Export tabel Gold: transaksi dengan anomaly flags.
    Hanya kolom yang relevan untuk dashboard.
    """
    export_cols = [
        "id_transaksi", "tahun_anggaran", "kota", "kode_skpd", "nama_skpd",
        "kode_rekening", "uraian_belanja", "pagu_anggaran", "realisasi",
        "persen_realisasi", "nama_vendor", "id_vendor", "tanggal_kontrak",
        "jenis_pengadaan",
    ]

    # Add scoring columns if they exist
    score_cols = [
        "benford_score", "benford_flag",
        "if_score_normalized", "if_anomaly",
        "stat_score", "stat_anomaly",
        "ensemble_score", "n_detectors_flagged", "risk_category", "is_flagged",
    ]

    available_cols = export_cols + [c for c in score_cols if c in df.columns]
    gold_df = df[available_cols].copy()

    # Sort: highest risk first
    if "ensemble_score" in gold_df.columns:
        gold_df = gold_df.sort_values("ensemble_score", ascending=False)

    out_path = GOLD_DIR / "gold_anomaly_transactions.csv"
    gold_df.to_csv(out_path, index=False)
    print(f"  [Gold] Anomaly transactions → {out_path} ({len(gold_df)} rows)")

    return gold_df


def export_vendor_risk_profile(df_vendors: pd.DataFrame) -> pd.DataFrame:
    """
    Export tabel Gold: profil risiko per vendor.
    """
    export_cols = [
        "id_vendor", "nama_vendor", "alamat", "nama_direktur",
        "npwp", "tahun_berdiri", "total_kontrak", "total_nilai_kontrak",
    ]

    risk_cols = [
        "entity_cluster_id", "is_in_cluster",
        "risk_shared_entity", "risk_new_big_contract",
        "risk_skpd_dominance", "risk_pagerank_anomaly",
        "graph_risk_score", "graph_risk_category",
    ]

    available_cols = [c for c in export_cols + risk_cols if c in df_vendors.columns]
    gold_df = df_vendors[available_cols].copy()

    # Sort by risk score
    if "graph_risk_score" in gold_df.columns:
        gold_df = gold_df.sort_values("graph_risk_score", ascending=False)

    out_path = GOLD_DIR / "gold_vendor_risk_profile.csv"
    gold_df.to_csv(out_path, index=False)
    print(f"  [Gold] Vendor risk profiles → {out_path} ({len(gold_df)} rows)")

    return gold_df


def export_skpd_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Export tabel Gold: ringkasan anomali per SKPD per kota.
    """
    # Aggregate per SKPD per kota
    agg_dict = {
        "id_transaksi": "count",
        "pagu_anggaran": "sum",
        "realisasi": "sum",
    }

    # Add anomaly counts if available
    if "is_flagged" in df.columns:
        agg_dict["is_flagged"] = "sum"
    if "ensemble_score" in df.columns:
        agg_dict["ensemble_score"] = "mean"

    summary = df.groupby(["kota", "kode_skpd", "nama_skpd"]).agg(agg_dict).reset_index()

    # Rename columns
    summary = summary.rename(columns={
        "id_transaksi": "total_transaksi",
        "pagu_anggaran": "total_pagu",
        "realisasi": "total_realisasi",
        "is_flagged": "jumlah_anomali",
        "ensemble_score": "rata_rata_risk_score",
    })

    # Calculate realisasi percentage
    summary["persen_realisasi_avg"] = (
        summary["total_realisasi"] / summary["total_pagu"] * 100
    ).round(2)

    # Anomaly rate
    if "jumlah_anomali" in summary.columns:
        summary["anomaly_rate"] = (
            summary["jumlah_anomali"] / summary["total_transaksi"] * 100
        ).round(2)

    # Sort by anomaly count
    sort_col = "jumlah_anomali" if "jumlah_anomali" in summary.columns else "total_realisasi"
    summary = summary.sort_values(sort_col, ascending=False)

    out_path = GOLD_DIR / "gold_skpd_summary.csv"
    summary.to_csv(out_path, index=False)
    print(f"  [Gold] SKPD summary → {out_path} ({len(summary)} rows)")

    return summary


def export_all_gold(
    df_transactions: pd.DataFrame,
    df_vendors: pd.DataFrame,
) -> dict:
    """
    Export semua tabel Gold layer.

    Returns
    -------
    dict
        Dictionary of gold DataFrames.
    """
    print("\n  Exporting to Gold Layer...")

    gold = {
        "anomaly_transactions": export_anomaly_transactions(df_transactions),
        "vendor_risk_profile": export_vendor_risk_profile(df_vendors),
        "skpd_summary": export_skpd_summary(df_transactions),
    }

    print(f"\n  ✅ All Gold tables exported to {GOLD_DIR}")

    return gold


if __name__ == "__main__":
    # Quick test
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data
    from ml_engine.data_generator.generate_vendor_network import generate_vendor_network

    df_trx = generate_apbd_data(save=False)
    df_vendor = generate_vendor_network(save=False)

    gold = export_all_gold(df_trx, df_vendor)
