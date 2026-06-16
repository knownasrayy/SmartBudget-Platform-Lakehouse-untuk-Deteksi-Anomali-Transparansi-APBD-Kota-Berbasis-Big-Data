"""
isolation_forest.py
=====================
Deteksi anomali transaksi APBD menggunakan Isolation Forest (scikit-learn).

Isolation Forest bekerja dengan prinsip: anomali mudah diisolasi
karena jumlahnya sedikit dan nilainya berbeda dari mayoritas.
Cocok untuk data belanja pemerintah yang besar dan tanpa label fraud.

Fitur:
- Feature engineering khusus APBD
- Isolation Forest model fitting
- Anomaly scoring (-1 to 0.5)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Optional
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    IF_N_ESTIMATORS,
    IF_CONTAMINATION,
    IF_RANDOM_STATE,
    ML_OUTPUT_DIR,
    SILVER_DIR,
    GOLD_DIR,
)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering untuk Isolation Forest.
    Menghasilkan fitur numerik yang merepresentasikan
    pola belanja normal vs anomali.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame transaksi APBD.

    Returns
    -------
    pd.DataFrame
        DataFrame asli + kolom fitur baru.
    """
    df = df.copy()

    # ---- Basic features ----
    # Log transformasi (normalisasi skala)
    df["log_realisasi"] = np.log1p(df["realisasi"].clip(lower=0))
    df["log_pagu"] = np.log1p(df["pagu_anggaran"].clip(lower=0))

    # Rasio realisasi terhadap pagu
    df["rasio_realisasi_pagu"] = df["realisasi"] / df["pagu_anggaran"].replace(0, np.nan)
    df["rasio_realisasi_pagu"] = df["rasio_realisasi_pagu"].fillna(0)

    # ---- Statistical features ----
    # Z-score realisasi per SKPD
    skpd_stats = df.groupby("kode_skpd")["realisasi"].agg(["mean", "std"]).reset_index()
    skpd_stats.columns = ["kode_skpd", "skpd_mean", "skpd_std"]
    df = df.merge(skpd_stats, on="kode_skpd", how="left")
    df["zscore_per_skpd"] = (df["realisasi"] - df["skpd_mean"]) / df["skpd_std"].replace(0, 1)
    df["zscore_per_skpd"] = df["zscore_per_skpd"].fillna(0)

    # Z-score realisasi per kode rekening
    rek_stats = df.groupby("kode_rekening")["realisasi"].agg(["mean", "std"]).reset_index()
    rek_stats.columns = ["kode_rekening", "rek_mean", "rek_std"]
    df = df.merge(rek_stats, on="kode_rekening", how="left")
    df["zscore_per_rekening"] = (df["realisasi"] - df["rek_mean"]) / df["rek_std"].replace(0, 1)
    df["zscore_per_rekening"] = df["zscore_per_rekening"].fillna(0)

    # ---- Temporal features ----
    df["tanggal_kontrak"] = pd.to_datetime(df["tanggal_kontrak"], errors="coerce")
    df["bulan_kontrak"] = df["tanggal_kontrak"].dt.month.fillna(6).astype(int)
    df["is_q4"] = (df["bulan_kontrak"] >= 10).astype(int)
    df["is_december"] = (df["bulan_kontrak"] == 12).astype(int)

    # ---- Round number detection ----
    def count_trailing_zeros(x):
        """Hitung trailing zeros (indikasi angka terlalu bulat)."""
        if x <= 0:
            return 0
        s = str(int(x))
        return len(s) - len(s.rstrip("0"))

    df["trailing_zeros_realisasi"] = df["realisasi"].apply(count_trailing_zeros)
    df["trailing_zeros_pagu"] = df["pagu_anggaran"].apply(count_trailing_zeros)

    # ---- Vendor features ----
    vendor_counts = df["id_vendor"].value_counts()
    df["vendor_kontrak_count"] = df["id_vendor"].map(vendor_counts)

    vendor_sum = df.groupby("id_vendor")["realisasi"].sum()
    df["vendor_total_nilai"] = df["id_vendor"].map(vendor_sum)

    # ---- Difference features ----
    df["selisih_pagu_realisasi"] = df["pagu_anggaran"] - df["realisasi"]
    df["log_selisih"] = np.log1p(df["selisih_pagu_realisasi"].clip(lower=0))

    # Clean up intermediate columns
    df.drop(columns=["skpd_mean", "skpd_std", "rek_mean", "rek_std"], inplace=True)

    return df


# Feature columns yang digunakan oleh Isolation Forest
FEATURE_COLUMNS = [
    "log_realisasi",
    "log_pagu",
    "rasio_realisasi_pagu",
    "zscore_per_skpd",
    "zscore_per_rekening",
    "is_q4",
    "is_december",
    "trailing_zeros_realisasi",
    "trailing_zeros_pagu",
    "vendor_kontrak_count",
    "log_selisih",
]


def run_isolation_forest(
    df: pd.DataFrame,
    feature_cols: Optional[list[str]] = None,
    n_estimators: int = IF_N_ESTIMATORS,
    contamination: float = IF_CONTAMINATION,
    random_state: int = IF_RANDOM_STATE,
    save: bool = True,
) -> pd.DataFrame:
    """
    Jalankan Isolation Forest pada data transaksi.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame yang sudah di-feature-engineering.
    feature_cols : list[str], optional
        Kolom fitur. Default: FEATURE_COLUMNS.
    n_estimators : int
        Jumlah decision trees.
    contamination : float
        Estimasi persentase anomali.
    random_state : int
        Random seed.
    save : bool
        Simpan hasil ke CSV.

    Returns
    -------
    pd.DataFrame
        DataFrame + kolom if_score dan if_anomaly.
    """
    print("\n" + "=" * 60)
    print("ISOLATION FOREST ANOMALY DETECTION")
    print("=" * 60)

    if feature_cols is None:
        feature_cols = FEATURE_COLUMNS

    # Feature engineering jika belum ada
    if "log_realisasi" not in df.columns:
        print("  Running feature engineering...")
        df = engineer_features(df)

    # Prepare feature matrix
    X = df[feature_cols].copy()
    X = X.fillna(0)

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"  Features : {len(feature_cols)} columns")
    print(f"  Samples  : {len(X_scaled)} transactions")
    print(f"  Config   : n_estimators={n_estimators}, contamination={contamination}")

    # Fit model
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )

    predictions = model.fit_predict(X_scaled)
    scores = model.decision_function(X_scaled)

    # Add results to dataframe
    df = df.copy()
    df["if_prediction"] = predictions          # 1 = normal, -1 = anomaly
    df["if_score"] = scores                     # Lower = more anomalous
    df["if_anomaly"] = predictions == -1        # Boolean flag

    # Normalize score to 0-1 range (1 = most anomalous)
    min_score, max_score = scores.min(), scores.max()
    if max_score > min_score:
        df["if_score_normalized"] = 1 - (scores - min_score) / (max_score - min_score)
    else:
        df["if_score_normalized"] = 0.0

    n_anomalies = df["if_anomaly"].sum()
    print(f"\n  Anomalies detected: {n_anomalies} ({n_anomalies/len(df)*100:.1f}%)")

    # Feature importance (based on depth)
    print("\n  Top features contributing to anomalies:")
    anomaly_mask = df["if_anomaly"]
    for col in feature_cols:
        normal_mean = df.loc[~anomaly_mask, col].mean()
        anomaly_mean = df.loc[anomaly_mask, col].mean()
        diff = abs(anomaly_mean - normal_mean)
        print(f"    {col:35s} | normal_mean={normal_mean:12.2f} | anomaly_mean={anomaly_mean:12.2f} | diff={diff:12.2f}")

    if save:
        out_path = ML_OUTPUT_DIR / "isolation_forest_results.csv"
        df[["id_transaksi", "if_prediction", "if_score", "if_score_normalized", "if_anomaly"]].to_csv(
            out_path, index=False
        )
        print(f"\n  Saved -> {out_path}")

        # Ekspor hasil prediksi Isolation Forest (kolom tambahan berisi skor anomali dan label Normal/Anomali)
        # lalu simpan outputnya ke folder data/gold/apbd_scored.csv.
        df_scored = df.copy()
        df_scored["anomaly_score"] = df_scored["if_score_normalized"]
        df_scored["anomaly_label"] = np.where(df_scored["if_anomaly"], "Anomali", "Normal")
        
        gold_out_path = GOLD_DIR / "apbd_scored.csv"
        df_scored.to_csv(gold_out_path, index=False)
        print(f"  Saved Gold Scored -> {gold_out_path}")

    return df


if __name__ == "__main__":
    # Wajib membaca data APBD bersih dari folder data/silver/ (hasil kerja Dimas)
    silver_path = SILVER_DIR / "silver_apbd_belanja.csv"
    if not silver_path.exists():
        raise FileNotFoundError(f"Data APBD bersih tidak ditemukan di {silver_path}. Jalankan pipeline lakehouse terlebih dahulu.")
        
    print(f"Membaca data APBD bersih dari {silver_path}...")
    df = pd.read_csv(silver_path)
    df = engineer_features(df)
    df = run_isolation_forest(df, save=True)

    print("\n--- Anomaly vs Ground Truth ---")
    if "is_anomaly_injected" in df.columns:
        ct = pd.crosstab(df["if_anomaly"], df["is_anomaly_injected"],
                         rownames=["IF_Detected"], colnames=["Ground_Truth"])
        print(ct)
