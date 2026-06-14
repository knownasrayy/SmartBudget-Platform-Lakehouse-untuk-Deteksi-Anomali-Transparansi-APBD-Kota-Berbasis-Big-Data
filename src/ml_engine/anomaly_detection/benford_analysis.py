"""
benford_analysis.py
=====================
Analisis Benford's Law pada data belanja APBD.

Hukum Benford menyatakan bahwa dalam data numerik yang natural,
digit pertama cenderung kecil (1 muncul ~30.1%, 9 muncul ~4.6%).
Deviasi signifikan dari distribusi ini mengindikasikan manipulasi data.

Fitur:
- First-digit analysis
- First-two-digit analysis
- Chi-square goodness-of-fit test
- Breakdown per SKPD & per kota
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    BENFORD_SIGNIFICANCE_LEVEL,
    BENFORD_MIN_SAMPLES,
    ML_OUTPUT_DIR,
)


# Distribusi Benford teoritis untuk digit pertama
BENFORD_EXPECTED = {
    d: np.log10(1 + 1 / d) for d in range(1, 10)
}

# Distribusi Benford untuk dua digit pertama (10-99)
BENFORD_TWO_DIGIT = {
    d: np.log10(1 + 1 / d) for d in range(10, 100)
}


def extract_first_digit(series: pd.Series) -> pd.Series:
    """
    Ekstrak digit pertama dari setiap nilai numerik.
    Mengabaikan nol, negatif, dan NaN.
    """
    abs_vals = series.abs().dropna()
    abs_vals = abs_vals[abs_vals > 0]
    first_digits = abs_vals.apply(lambda x: int(str(int(x))[0]))
    return first_digits


def extract_first_two_digits(series: pd.Series) -> pd.Series:
    """Ekstrak dua digit pertama dari setiap nilai numerik."""
    abs_vals = series.abs().dropna()
    abs_vals = abs_vals[abs_vals >= 10]
    two_digits = abs_vals.apply(lambda x: int(str(int(x))[:2]))
    return two_digits


def benford_test(
    values: pd.Series,
    column_name: str = "value",
    alpha: float = BENFORD_SIGNIFICANCE_LEVEL,
) -> dict:
    """
    Lakukan Benford's Law test pada serangkaian nilai.

    Parameters
    ----------
    values : pd.Series
        Seri nilai numerik untuk dianalisis.
    column_name : str
        Nama kolom (untuk labeling output).
    alpha : float
        Significance level untuk chi-square test.

    Returns
    -------
    dict
        Hasil analisis termasuk distribusi, chi-square stat, p-value, dan verdict.
    """
    first_digits = extract_first_digit(values)

    if len(first_digits) < BENFORD_MIN_SAMPLES:
        return {
            "column": column_name,
            "n_samples": len(first_digits),
            "status": "INSUFFICIENT_DATA",
            "chi2_stat": None,
            "p_value": None,
            "is_suspicious": False,
            "observed_dist": {},
            "expected_dist": BENFORD_EXPECTED,
            "deviations": {},
        }

    # Hitung distribusi observasi
    observed_counts = first_digits.value_counts().sort_index()
    total = len(first_digits)

    observed_dist = {}
    expected_counts = {}
    for d in range(1, 10):
        observed_dist[d] = observed_counts.get(d, 0) / total
        expected_counts[d] = BENFORD_EXPECTED[d] * total

    # Chi-square test
    obs_arr = [observed_counts.get(d, 0) for d in range(1, 10)]
    exp_arr = [expected_counts[d] for d in range(1, 10)]

    chi2_stat, p_value = stats.chisquare(obs_arr, f_exp=exp_arr)

    # Deviasi per digit
    deviations = {}
    for d in range(1, 10):
        deviations[d] = round(observed_dist[d] - BENFORD_EXPECTED[d], 4)

    # Maximum Absolute Deviation (MAD)
    mad = np.mean([abs(deviations[d]) for d in range(1, 10)])

    # Verdict
    is_suspicious = p_value < alpha

    return {
        "column": column_name,
        "n_samples": total,
        "status": "ANALYZED",
        "chi2_stat": round(chi2_stat, 4),
        "p_value": round(p_value, 6),
        "mad": round(mad, 4),
        "is_suspicious": is_suspicious,
        "verdict": "SUSPICIOUS" if is_suspicious else "CONFORMING",
        "observed_dist": {k: round(v, 4) for k, v in observed_dist.items()},
        "expected_dist": {k: round(v, 4) for k, v in BENFORD_EXPECTED.items()},
        "deviations": deviations,
    }


def benford_analysis_by_group(
    df: pd.DataFrame,
    value_column: str = "realisasi",
    group_column: str = "nama_skpd",
    alpha: float = BENFORD_SIGNIFICANCE_LEVEL,
) -> pd.DataFrame:
    """
    Lakukan Benford analysis per grup (SKPD, kota, dll).

    Returns
    -------
    pd.DataFrame
        Tabel dengan skor deviasi per grup, sorted by suspiciousness.
    """
    results = []

    for group_name, group_df in df.groupby(group_column):
        result = benford_test(group_df[value_column], column_name=str(group_name), alpha=alpha)
        result["group_column"] = group_column
        result["group_value"] = group_name
        results.append(result)

    results_df = pd.DataFrame(results)

    # Sort by MAD descending (paling menyimpang di atas)
    if "mad" in results_df.columns:
        results_df = results_df.sort_values("mad", ascending=False)

    return results_df


def flag_benford_anomalies(
    df: pd.DataFrame,
    value_column: str = "realisasi",
    alpha: float = BENFORD_SIGNIFICANCE_LEVEL,
) -> pd.DataFrame:
    """
    Flag individual transaksi berdasarkan Benford analysis.

    Strategi: Jika first-digit dari nilai transaksi adalah digit yang
    over-represented (deviasi positif besar), maka flag sebagai suspicious.

    Returns
    -------
    pd.DataFrame
        DataFrame asli + kolom benford_flag dan benford_score.
    """
    df = df.copy()

    # Global Benford test
    result = benford_test(df[value_column], column_name=value_column)

    # Calculate per-digit anomaly score
    first_digits = extract_first_digit(df[value_column])

    # Assign Benford score berdasarkan seberapa besar deviasi digit-nya
    digit_scores = {}
    if result["status"] == "ANALYZED":
        max_dev = max(abs(v) for v in result["deviations"].values()) if result["deviations"] else 1
        for d in range(1, 10):
            dev = result["deviations"].get(d, 0)
            # Positive deviation = over-represented = more suspicious
            digit_scores[d] = max(0, dev / max_dev) if max_dev > 0 else 0
    else:
        digit_scores = {d: 0 for d in range(1, 10)}

    # Map scores to transactions
    df["benford_first_digit"] = df[value_column].apply(
        lambda x: int(str(int(abs(x)))[0]) if pd.notna(x) and x > 0 else 0
    )
    df["benford_score"] = df["benford_first_digit"].map(digit_scores).fillna(0)
    df["benford_flag"] = df["benford_score"] > 0.5  # Threshold

    return df


def run_benford_analysis(
    df: pd.DataFrame,
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Jalankan full Benford analysis pipeline.

    Returns
    -------
    tuple
        (df_flagged, results_by_skpd, results_by_kota)
    """
    print("\n" + "=" * 60)
    print("BENFORD'S LAW ANALYSIS")
    print("=" * 60)

    # 1. Global test
    print("\n--- Global Analysis ---")
    global_realisasi = benford_test(df["realisasi"], "realisasi")
    global_pagu = benford_test(df["pagu_anggaran"], "pagu_anggaran")
    print(f"  Realisasi : chi²={global_realisasi['chi2_stat']}, p={global_realisasi['p_value']}, "
          f"verdict={global_realisasi['verdict']}")
    print(f"  Pagu      : chi²={global_pagu['chi2_stat']}, p={global_pagu['p_value']}, "
          f"verdict={global_pagu['verdict']}")

    # 2. Per SKPD
    print("\n--- Per SKPD Analysis ---")
    results_skpd = benford_analysis_by_group(df, "realisasi", "nama_skpd")
    suspicious_skpd = results_skpd[results_skpd["is_suspicious"] == True]
    print(f"  Suspicious SKPD: {len(suspicious_skpd)}/{len(results_skpd)}")

    # 3. Per Kota
    print("\n--- Per Kota Analysis ---")
    results_kota = benford_analysis_by_group(df, "realisasi", "kota")
    suspicious_kota = results_kota[results_kota["is_suspicious"] == True]
    print(f"  Suspicious kota: {len(suspicious_kota)}/{len(results_kota)}")

    # 4. Flag individual transactions
    df_flagged = flag_benford_anomalies(df)
    n_flagged = df_flagged["benford_flag"].sum()
    print(f"\n  Transactions flagged by Benford: {n_flagged} ({n_flagged/len(df)*100:.1f}%)")

    if save:
        results_skpd.to_csv(ML_OUTPUT_DIR / "benford_results_skpd.csv", index=False)
        results_kota.to_csv(ML_OUTPUT_DIR / "benford_results_kota.csv", index=False)
        print(f"  Saved results to {ML_OUTPUT_DIR}")

    return df_flagged, results_skpd, results_kota


if __name__ == "__main__":
    # Quick test with synthetic data
    from ml_engine.data_generator.generate_apbd_synthetic import generate_apbd_data

    df = generate_apbd_data(save=False)
    df_flagged, res_skpd, res_kota = run_benford_analysis(df)

    print("\n--- Top Suspicious SKPD ---")
    print(res_skpd.head(5)[["group_value", "mad", "p_value", "verdict"]].to_string())
