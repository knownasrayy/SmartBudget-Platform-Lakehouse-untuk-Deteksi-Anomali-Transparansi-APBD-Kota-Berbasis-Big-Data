"""
ensemble.py
=============
Ensemble detector — menggabungkan sinyal dari Benford, Isolation Forest,
dan Z-Score menjadi satu risk score terpadu.

Strategi:
1. Voting: Jika ≥ 2/3 detector flag anomali → High Risk
2. Weighted score: Score akhir = weighted average dari semua detector
3. Risk category: Low / Medium / High / Critical
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    ENSEMBLE_WEIGHTS,
    RISK_THRESHOLDS,
    ML_OUTPUT_DIR,
)


def compute_ensemble_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hitung ensemble risk score dari semua detector.

    Membutuhkan kolom:
    - benford_score (0-1 dari Benford analysis)
    - if_score_normalized (0-1 dari Isolation Forest)
    - stat_score (0-1 dari Z-Score/IQR/Percentage)

    Returns
    -------
    pd.DataFrame
        DataFrame + kolom ensemble_score, risk_category, dll.
    """
    df = df.copy()

    # Pastikan semua score columns ada
    score_columns = {
        "benford_score": ENSEMBLE_WEIGHTS["benford"],
        "if_score_normalized": ENSEMBLE_WEIGHTS["isolation_forest"],
        "stat_score": ENSEMBLE_WEIGHTS["zscore"],
    }

    for col in score_columns:
        if col not in df.columns:
            print(f"  [WARNING] Column '{col}' not found, using 0")
            df[col] = 0.0

    # Weighted average score (0-100)
    df["ensemble_score"] = 0.0
    for col, weight in score_columns.items():
        df["ensemble_score"] += df[col] * weight * 100

    df["ensemble_score"] = df["ensemble_score"].clip(0, 100).round(2)

    # Voting system
    flag_columns = []
    for col_name, flag_col in [
        ("benford_flag", "benford_flag"),
        ("if_anomaly", "if_anomaly"),
        ("stat_anomaly", "stat_anomaly"),
    ]:
        if flag_col in df.columns:
            flag_columns.append(flag_col)

    if flag_columns:
        df["n_detectors_flagged"] = df[flag_columns].sum(axis=1)
    else:
        df["n_detectors_flagged"] = 0

    # Risk category
    def _categorize_risk(row):
        score = row["ensemble_score"]
        n_flags = row["n_detectors_flagged"]

        # Jika ≥ 2 detector flag → minimal Medium
        if n_flags >= 3:
            return "CRITICAL"
        elif n_flags >= 2 and score >= RISK_THRESHOLDS["medium"]:
            return "HIGH"
        elif score >= RISK_THRESHOLDS["high"]:
            return "CRITICAL"
        elif score >= RISK_THRESHOLDS["medium"]:
            return "HIGH"
        elif score >= RISK_THRESHOLDS["low"]:
            return "MEDIUM"
        else:
            return "LOW"

    df["risk_category"] = df.apply(_categorize_risk, axis=1)

    # Boolean flag
    df["is_flagged"] = df["risk_category"].isin(["HIGH", "CRITICAL"])

    return df


def run_ensemble(
    df: pd.DataFrame,
    save: bool = True,
) -> pd.DataFrame:
    """
    Jalankan ensemble scoring.

    Returns
    -------
    pd.DataFrame
        DataFrame + ensemble columns.
    """
    print("\n" + "=" * 60)
    print("ENSEMBLE RISK SCORING")
    print("=" * 60)

    df = compute_ensemble_score(df)

    # Summary statistics
    risk_dist = df["risk_category"].value_counts()
    print("\n  Risk Category Distribution:")
    for cat in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = risk_dist.get(cat, 0)
        pct = count / len(df) * 100
        print(f"    {cat:10s} : {count:5d} ({pct:5.1f}%)")

    print(f"\n  Ensemble Score Stats:")
    print(f"    Mean   : {df['ensemble_score'].mean():.2f}")
    print(f"    Median : {df['ensemble_score'].median():.2f}")
    print(f"    Max    : {df['ensemble_score'].max():.2f}")

    # Detector agreement analysis
    if "n_detectors_flagged" in df.columns:
        print(f"\n  Detector Agreement:")
        agreement = df["n_detectors_flagged"].value_counts().sort_index()
        for n_flags, count in agreement.items():
            print(f"    {int(n_flags)} detectors agree: {count} transactions")

    # Ground truth comparison (if available)
    if "is_anomaly_injected" in df.columns:
        print(f"\n  --- Ground Truth Comparison ---")
        tp = ((df["is_flagged"]) & (df["is_anomaly_injected"])).sum()
        fp = ((df["is_flagged"]) & (~df["is_anomaly_injected"])).sum()
        fn = ((~df["is_flagged"]) & (df["is_anomaly_injected"])).sum()
        tn = ((~df["is_flagged"]) & (~df["is_anomaly_injected"])).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        print(f"    True Positives  : {tp}")
        print(f"    False Positives : {fp}")
        print(f"    False Negatives : {fn}")
        print(f"    True Negatives  : {tn}")
        print(f"    Precision       : {precision:.3f}")
        print(f"    Recall          : {recall:.3f}")
        print(f"    F1 Score        : {f1:.3f}")

    if save:
        out_cols = [
            "id_transaksi", "ensemble_score", "n_detectors_flagged",
            "risk_category", "is_flagged",
        ]
        # Add individual scores if present
        for col in ["benford_score", "if_score_normalized", "stat_score"]:
            if col in df.columns:
                out_cols.append(col)

        df[out_cols].to_csv(ML_OUTPUT_DIR / "ensemble_results.csv", index=False)
        print(f"\n  Saved → {ML_OUTPUT_DIR / 'ensemble_results.csv'}")

    return df


if __name__ == "__main__":
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data
    from ml_engine.anomaly_detection.benford_analysis import run_benford_analysis
    from ml_engine.anomaly_detection.isolation_forest import engineer_features, run_isolation_forest
    from ml_engine.anomaly_detection.zscore_detector import run_zscore_detection

    df = generate_apbd_data(save=False)
    df, _, _ = run_benford_analysis(df, save=False)
    df = engineer_features(df)
    df = run_isolation_forest(df, save=False)
    df = run_zscore_detection(df, save=False)
    df = run_ensemble(df)
