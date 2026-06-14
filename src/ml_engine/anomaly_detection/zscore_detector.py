"""
zscore_detector.py
====================
Deteksi anomali berbasis statistik klasik (Z-Score dan IQR).

Metode sederhana tapi efektif sebagai baseline dan
komplemen untuk Isolation Forest.

Fitur:
- Z-Score outlier detection per kategori
- IQR-based outlier detection
- Realisasi percentage range check
"""

import pandas as pd
import numpy as np
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    ZSCORE_THRESHOLD,
    IQR_MULTIPLIER,
    ML_OUTPUT_DIR,
)


def zscore_detection(
    df: pd.DataFrame,
    value_column: str = "realisasi",
    group_column: str = "kode_rekening",
    threshold: float = ZSCORE_THRESHOLD,
) -> pd.DataFrame:
    """
    Deteksi outlier menggunakan Z-Score per grup.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame transaksi.
    value_column : str
        Kolom nilai yang dianalisis.
    group_column : str
        Kolom untuk grouping (outlier relatif per kategori).
    threshold : float
        Threshold Z-Score (default: 3.0).

    Returns
    -------
    pd.DataFrame
        DataFrame + kolom zscore_value dan zscore_flag.
    """
    df = df.copy()

    # Calculate z-score per group
    group_stats = df.groupby(group_column)[value_column].agg(["mean", "std"]).reset_index()
    group_stats.columns = [group_column, "_zs_mean", "_zs_std"]

    df = df.merge(group_stats, on=group_column, how="left")

    df["zscore_value"] = (df[value_column] - df["_zs_mean"]) / df["_zs_std"].replace(0, 1)
    df["zscore_value"] = df["zscore_value"].fillna(0)
    df["zscore_flag"] = df["zscore_value"].abs() > threshold

    # Cleanup
    df.drop(columns=["_zs_mean", "_zs_std"], inplace=True)

    return df


def iqr_detection(
    df: pd.DataFrame,
    value_column: str = "realisasi",
    group_column: str = "kode_rekening",
    multiplier: float = IQR_MULTIPLIER,
) -> pd.DataFrame:
    """
    Deteksi outlier menggunakan IQR (Interquartile Range) per grup.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame transaksi.
    value_column : str
        Kolom nilai.
    group_column : str
        Kolom grouping.
    multiplier : float
        IQR multiplier (default: 1.5).

    Returns
    -------
    pd.DataFrame
        DataFrame + kolom iqr_flag.
    """
    df = df.copy()

    def _iqr_bounds(group):
        q1 = group[value_column].quantile(0.25)
        q3 = group[value_column].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        group["iqr_lower"] = lower
        group["iqr_upper"] = upper
        group["iqr_flag"] = (group[value_column] < lower) | (group[value_column] > upper)
        return group

    df = df.groupby(group_column, group_keys=False).apply(_iqr_bounds)
    df.drop(columns=["iqr_lower", "iqr_upper"], inplace=True)

    return df


def percentage_range_check(
    df: pd.DataFrame,
    persen_column: str = "persen_realisasi",
    low_threshold: float = 20.0,
    high_threshold: float = 100.0,
) -> pd.DataFrame:
    """
    Flag transaksi dengan persentase realisasi di luar range normal.

    - < 20% → kemungkinan "anggaran siluman" (dialokasikan tapi tidak digunakan)
    - > 100% → overbudget / realisasi melebihi pagu

    Returns
    -------
    pd.DataFrame
        DataFrame + kolom persen_flag.
    """
    df = df.copy()

    df["persen_too_low"] = df[persen_column] < low_threshold
    df["persen_too_high"] = df[persen_column] > high_threshold
    df["persen_flag"] = df["persen_too_low"] | df["persen_too_high"]

    return df


def run_zscore_detection(
    df: pd.DataFrame,
    save: bool = True,
) -> pd.DataFrame:
    """
    Jalankan semua metode deteksi statistik.

    Returns
    -------
    pd.DataFrame
        DataFrame + semua flag statistik + combined zscore_anomaly score.
    """
    print("\n" + "=" * 60)
    print("Z-SCORE & STATISTICAL ANOMALY DETECTION")
    print("=" * 60)

    # 1. Z-Score per kode rekening
    print("\n--- Z-Score Detection ---")
    df = zscore_detection(df, "realisasi", "kode_rekening")
    n_zscore = df["zscore_flag"].sum()
    print(f"  Z-Score outliers (|z| > {ZSCORE_THRESHOLD}): {n_zscore} ({n_zscore/len(df)*100:.1f}%)")

    # 2. IQR per kode rekening
    print("\n--- IQR Detection ---")
    df = iqr_detection(df, "realisasi", "kode_rekening")
    n_iqr = df["iqr_flag"].sum()
    print(f"  IQR outliers: {n_iqr} ({n_iqr/len(df)*100:.1f}%)")

    # 3. Percentage range check
    print("\n--- Percentage Range Check ---")
    df = percentage_range_check(df)
    n_low = df["persen_too_low"].sum()
    n_high = df["persen_too_high"].sum()
    print(f"  Too low  (< 20%): {n_low}")
    print(f"  Too high (>100%): {n_high}")

    # Combined statistical score (0-1)
    stat_flags = ["zscore_flag", "iqr_flag", "persen_flag"]
    df["stat_score"] = df[stat_flags].sum(axis=1) / len(stat_flags)
    df["stat_anomaly"] = df["stat_score"] > 0.33  # At least 1 of 3 flags

    n_stat = df["stat_anomaly"].sum()
    print(f"\n  Combined statistical anomalies: {n_stat} ({n_stat/len(df)*100:.1f}%)")

    if save:
        out_cols = ["id_transaksi", "zscore_value", "zscore_flag", "iqr_flag",
                    "persen_flag", "stat_score", "stat_anomaly"]
        df[out_cols].to_csv(ML_OUTPUT_DIR / "zscore_results.csv", index=False)
        print(f"  Saved → {ML_OUTPUT_DIR / 'zscore_results.csv'}")

    return df


if __name__ == "__main__":
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data

    df = generate_apbd_data(save=False)
    df = run_zscore_detection(df)

    print("\n--- Statistical vs Ground Truth ---")
    if "is_anomaly_injected" in df.columns:
        ct = pd.crosstab(df["stat_anomaly"], df["is_anomaly_injected"],
                         rownames=["Stat_Detected"], colnames=["Ground_Truth"])
        print(ct)
