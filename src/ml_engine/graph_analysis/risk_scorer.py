"""
risk_scorer.py
================
Graph-based risk scoring untuk setiap vendor.

Menghitung skor risiko berdasarkan:
1. Shared address/direktur (shell company indicator)
2. Vendor baru dengan kontrak besar
3. Dominasi di SKPD tertentu
4. High PageRank tapi sedikit kontrak (intermediary)
5. Community-level risk (komunitas dengan banyak anomali)
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    GRAPH_RISK_WEIGHTS,
    ML_OUTPUT_DIR,
)


def score_shared_entities(
    df_vendors: pd.DataFrame,
    entity_pairs: pd.DataFrame,
) -> pd.Series:
    """
    Skor risiko berdasarkan jumlah shared address/director.

    Returns
    -------
    pd.Series
        Skor per vendor_id.
    """
    scores = pd.Series(0.0, index=df_vendors["id_vendor"])

    if entity_pairs.empty:
        return scores

    # Count shared connections per vendor
    for _, pair in entity_pairs.iterrows():
        match_type = pair["match_type"]
        weight = GRAPH_RISK_WEIGHTS.get("shared_address", 30) if match_type == "shared_address" \
            else GRAPH_RISK_WEIGHTS.get("shared_director", 30)

        if pair["vendor_1"] in scores.index:
            scores[pair["vendor_1"]] += weight
        if pair["vendor_2"] in scores.index:
            scores[pair["vendor_2"]] += weight

    # Normalize to 0-100
    max_score = scores.max()
    if max_score > 0:
        scores = (scores / max_score) * 100

    return scores


def score_new_vendor_big_contract(
    df_vendors: pd.DataFrame,
    current_year: int = 2025,
    age_threshold: int = 2,
    value_percentile: float = 0.75,
) -> pd.Series:
    """
    Skor risiko: vendor baru (<2 tahun) dengan kontrak besar.

    Returns
    -------
    pd.Series
        Skor per vendor_id.
    """
    scores = pd.Series(0.0, index=df_vendors["id_vendor"])

    age = current_year - df_vendors["tahun_berdiri"]
    is_new = age <= age_threshold

    value_threshold = df_vendors["total_nilai_kontrak"].quantile(value_percentile)
    is_big = df_vendors["total_nilai_kontrak"] >= value_threshold

    suspicious = is_new & is_big
    weight = GRAPH_RISK_WEIGHTS.get("new_vendor_big_contract", 20)

    scores[df_vendors.loc[suspicious, "id_vendor"]] = weight

    return scores


def score_skpd_dominance(
    df_transactions: pd.DataFrame,
    dominance_threshold: float = 0.30,
) -> pd.Series:
    """
    Skor risiko: vendor yang mendominasi kontrak di satu SKPD (>30%).

    Returns
    -------
    pd.Series
        Skor per vendor_id.
    """
    vendor_ids = df_transactions["id_vendor"].unique()
    scores = pd.Series(0.0, index=vendor_ids)

    # Hitung share per vendor per SKPD
    skpd_vendor = df_transactions.groupby(["kode_skpd", "id_vendor"])["realisasi"].sum().reset_index()
    skpd_total = df_transactions.groupby("kode_skpd")["realisasi"].sum().reset_index()
    skpd_total.columns = ["kode_skpd", "total_skpd"]

    skpd_vendor = skpd_vendor.merge(skpd_total, on="kode_skpd")
    skpd_vendor["share"] = skpd_vendor["realisasi"] / skpd_vendor["total_skpd"]

    # Flag vendors yang menguasai >threshold di satu SKPD
    dominant = skpd_vendor[skpd_vendor["share"] > dominance_threshold]
    weight = GRAPH_RISK_WEIGHTS.get("dominant_in_skpd", 25)

    for _, row in dominant.iterrows():
        vid = row["id_vendor"]
        if vid in scores.index:
            scores[vid] = max(scores[vid], weight * row["share"])

    return scores


def score_pagerank_anomaly(
    centrality_df: pd.DataFrame,
    df_vendors: pd.DataFrame,
    pagerank_percentile: float = 0.90,
    contract_percentile: float = 0.25,
) -> pd.Series:
    """
    Skor risiko: vendor dengan PageRank tinggi tapi sedikit kontrak.
    Ini mengindikasikan vendor perantara (intermediary).

    Returns
    -------
    pd.Series
        Skor per vendor_id.
    """
    scores = pd.Series(0.0, index=df_vendors["id_vendor"])

    vendor_centrality = centrality_df[centrality_df["node_type"] == "Vendor"].copy()
    if vendor_centrality.empty:
        return scores

    pr_threshold = vendor_centrality["pagerank"].quantile(pagerank_percentile)
    high_pr = vendor_centrality[vendor_centrality["pagerank"] >= pr_threshold]

    # Merge with vendor data for contract counts
    merged = high_pr.merge(
        df_vendors[["id_vendor", "total_kontrak"]],
        left_on="node_id",
        right_on="id_vendor",
        how="left",
    )

    if "total_kontrak" in merged.columns:
        contract_thresh = df_vendors["total_kontrak"].quantile(contract_percentile)
        intermediaries = merged[merged["total_kontrak"] <= contract_thresh]

        weight = GRAPH_RISK_WEIGHTS.get("high_pagerank_low_contracts", 25)
        for _, row in intermediaries.iterrows():
            vid = row["id_vendor"]
            if vid in scores.index:
                scores[vid] = weight

    return scores


def compute_vendor_risk_scores(
    df_vendors: pd.DataFrame,
    df_transactions: pd.DataFrame,
    entity_pairs: pd.DataFrame,
    centrality_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Hitung skor risiko gabungan untuk setiap vendor.

    Returns
    -------
    pd.DataFrame
        df_vendors + kolom risk scores.
    """
    df = df_vendors.copy()

    # Individual risk components
    df["risk_shared_entity"] = score_shared_entities(df_vendors, entity_pairs).values
    df["risk_new_big_contract"] = score_new_vendor_big_contract(df_vendors).values
    df["risk_skpd_dominance"] = score_skpd_dominance(df_transactions).reindex(df["id_vendor"]).fillna(0).values
    df["risk_pagerank_anomaly"] = score_pagerank_anomaly(centrality_df, df_vendors).values

    # Combined risk score (0-100)
    risk_components = [
        "risk_shared_entity",
        "risk_new_big_contract",
        "risk_skpd_dominance",
        "risk_pagerank_anomaly",
    ]

    df["graph_risk_score"] = df[risk_components].sum(axis=1)
    df["graph_risk_score"] = df["graph_risk_score"].clip(0, 100).round(2)

    # Risk category
    def _categorize(score):
        if score >= 75:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        else:
            return "LOW"

    df["graph_risk_category"] = df["graph_risk_score"].apply(_categorize)

    return df


def run_risk_scoring(
    df_vendors: pd.DataFrame,
    df_transactions: pd.DataFrame,
    entity_pairs: pd.DataFrame,
    centrality_df: pd.DataFrame,
    save: bool = True,
) -> pd.DataFrame:
    """
    Jalankan full risk scoring pipeline.

    Returns
    -------
    pd.DataFrame
        Vendor DataFrame + risk scores.
    """
    print("\n" + "=" * 60)
    print("GRAPH-BASED VENDOR RISK SCORING")
    print("=" * 60)

    df = compute_vendor_risk_scores(df_vendors, df_transactions, entity_pairs, centrality_df)

    # Summary
    risk_dist = df["graph_risk_category"].value_counts()
    print("\n  Vendor Risk Distribution:")
    for cat in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = risk_dist.get(cat, 0)
        pct = count / len(df) * 100
        print(f"    {cat:10s} : {count:4d} ({pct:5.1f}%)")

    print(f"\n  Risk Score Stats:")
    print(f"    Mean   : {df['graph_risk_score'].mean():.2f}")
    print(f"    Median : {df['graph_risk_score'].median():.2f}")
    print(f"    Max    : {df['graph_risk_score'].max():.2f}")

    # Top risky vendors
    top_risky = df.nlargest(10, "graph_risk_score")
    print(f"\n  Top 10 Risky Vendors:")
    for _, row in top_risky.iterrows():
        print(f"    {row['id_vendor']:10s} | {row['nama_vendor']:35s} | "
              f"score={row['graph_risk_score']:6.1f} | {row['graph_risk_category']}")

    # Ground truth comparison
    if "is_fraud_vendor" in df.columns:
        print(f"\n  --- Ground Truth Comparison ---")
        flagged = df["graph_risk_category"].isin(["HIGH", "CRITICAL"])
        tp = (flagged & df["is_fraud_vendor"]).sum()
        fp = (flagged & ~df["is_fraud_vendor"]).sum()
        fn = (~flagged & df["is_fraud_vendor"]).sum()
        tn = (~flagged & ~df["is_fraud_vendor"]).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        print(f"    Precision : {precision:.3f}")
        print(f"    Recall    : {recall:.3f}")
        print(f"    F1 Score  : {f1:.3f}")

    if save:
        out_path = ML_OUTPUT_DIR / "vendor_risk_scores.csv"
        df.to_csv(out_path, index=False)
        print(f"\n  Saved → {out_path}")

    return df


if __name__ == "__main__":
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data
    from ml_engine.data_generator.generate_vendor_network import generate_vendor_network
    from ml_engine.graph_analysis.neo4j_loader import build_graph
    from ml_engine.graph_analysis.entity_resolver import run_entity_resolution
    from ml_engine.graph_analysis.community_detector import run_community_detection

    df_trx = generate_apbd_data(save=False)
    df_vendor = generate_vendor_network(save=False)
    G = build_graph(df_trx, df_vendor)
    df_vendor, entity_pairs = run_entity_resolution(df_vendor, save=False)
    centrality_df, communities = run_community_detection(G, save=False)
    df_risk = run_risk_scoring(df_vendor, df_trx, entity_pairs, centrality_df)
