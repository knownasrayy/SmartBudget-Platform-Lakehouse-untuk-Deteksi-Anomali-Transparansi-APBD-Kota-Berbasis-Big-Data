"""
generate_apbd_synthetic.py
===========================
Generator data sintetis APBD belanja yang realistis.
Mensimulasikan data Silver layer (output dari Lakehouse Engineer)
agar ML Engineer bisa bekerja mandiri.

Fitur:
- Data mengikuti struktur SIPD/SIKD nyata
- ~5% anomali di-inject secara terukur (ground truth)
- Distribusi nilai mengikuti pola belanja pemerintah realistis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    SILVER_DIR,
    KOTA_LIST,
    SKPD_LIST,
    KODE_REKENING_BELANJA,
    JENIS_PENGADAAN,
    SYNTHETIC_NUM_TRANSACTIONS,
    SYNTHETIC_ANOMALY_RATE,
    SYNTHETIC_YEARS,
    RANDOM_SEED,
)


def _generate_vendor_name(rng: np.random.Generator) -> str:
    """Generate nama vendor/perusahaan realistis Indonesia."""
    prefixes = [
        "PT", "CV", "PT", "PT", "CV", "PT", "UD", "PT",
    ]
    words_1 = [
        "Cipta", "Karya", "Mitra", "Surya", "Bumi", "Adi",
        "Mega", "Indo", "Prima", "Jaya", "Eka", "Tri",
        "Cahaya", "Sinar", "Global", "Nusa", "Putra", "Mandiri",
        "Abadi", "Mulia", "Sejahtera", "Makmur", "Sentosa", "Utama",
    ]
    words_2 = [
        "Sejahtera", "Mandiri", "Perkasa", "Abadi", "Lestari",
        "Sentosa", "Pratama", "Utama", "Makmur", "Jaya",
        "Konstruksi", "Teknologi", "Konsultindo", "Perkasa", "Gemilang",
        "Nusantara", "Indonesia", "Persada", "Solusi", "Kreasi",
    ]
    prefix = rng.choice(prefixes)
    w1 = rng.choice(words_1)
    w2 = rng.choice(words_2)
    return f"{prefix} {w1} {w2}"


def _generate_pagu_realistis(kode_rekening: str, rng: np.random.Generator) -> float:
    """
    Generate nilai pagu yang realistis berdasarkan jenis rekening.
    Belanja modal cenderung lebih besar dari belanja barang/pegawai.
    """
    ranges = {
        "5.1": (50_000_000, 2_000_000_000),      # Belanja Pegawai: 50jt - 2M
        "5.2": (10_000_000, 5_000_000_000),       # Belanja Barang: 10jt - 5M
        "5.3": (100_000_000, 50_000_000_000),     # Belanja Modal: 100jt - 50M
        "5.4": (25_000_000, 10_000_000_000),      # Hibah/Bansos: 25jt - 10M
    }

    prefix = kode_rekening[:3]
    low, high = ranges.get(prefix, (10_000_000, 1_000_000_000))

    # Log-normal distribution untuk simulasi distribusi belanja pemerintah
    mu = np.log(np.sqrt(low * high))
    sigma = (np.log(high) - np.log(low)) / 4
    value = rng.lognormal(mu, sigma)

    # Clip ke range yang masuk akal
    value = np.clip(value, low, high)

    # Bulatkan ke ribuan (realistis untuk anggaran pemerintah)
    return round(value / 1000) * 1000


def _generate_normal_transaction(
    idx: int,
    rng: np.random.Generator,
    vendor_pool: list[str],
    vendor_id_map: dict[str, str],
) -> dict:
    """Generate satu transaksi normal (non-anomali)."""
    kota = rng.choice(KOTA_LIST)
    skpd = rng.choice(SKPD_LIST)
    tahun = rng.choice(SYNTHETIC_YEARS)
    kode_rek = rng.choice(list(KODE_REKENING_BELANJA.keys()))
    uraian = KODE_REKENING_BELANJA[kode_rek]
    jenis = rng.choice(JENIS_PENGADAAN)
    vendor = rng.choice(vendor_pool)

    pagu = _generate_pagu_realistis(kode_rek, rng)

    # Realisasi normal: 60-98% dari pagu
    persen = rng.uniform(0.60, 0.98)
    realisasi = round(pagu * persen / 1000) * 1000

    # Tanggal kontrak: tersebar sepanjang tahun, sedikit bias ke Q1-Q3
    month = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                       p=[0.10, 0.10, 0.12, 0.10, 0.09, 0.09,
                          0.08, 0.08, 0.07, 0.07, 0.05, 0.05])
    day = rng.integers(1, 29)
    tanggal = datetime(tahun, month, day)

    return {
        "id_transaksi": f"TRX-{tahun}-{idx:05d}",
        "tahun_anggaran": tahun,
        "kota": kota,
        "kode_skpd": skpd["kode"],
        "nama_skpd": skpd["nama"],
        "kode_rekening": kode_rek,
        "uraian_belanja": uraian,
        "pagu_anggaran": pagu,
        "realisasi": realisasi,
        "persen_realisasi": round(realisasi / pagu * 100, 2),
        "nama_vendor": vendor,
        "id_vendor": vendor_id_map[vendor],
        "tanggal_kontrak": tanggal.strftime("%Y-%m-%d"),
        "jenis_pengadaan": jenis,
        "is_anomaly_injected": False,
        "anomaly_type": "none",
    }


def _inject_anomaly(transaction: dict, anomaly_type: str, rng: np.random.Generator) -> dict:
    """
    Inject anomali ke transaksi yang sudah ada.
    Mengembalikan transaksi yang telah dimodifikasi + label ground truth.
    """
    t = transaction.copy()
    t["is_anomaly_injected"] = True
    t["anomaly_type"] = anomaly_type

    if anomaly_type == "overbudget":
        # Realisasi melebihi pagu (105-180%)
        multiplier = rng.uniform(1.05, 1.80)
        t["realisasi"] = round(t["pagu_anggaran"] * multiplier / 1000) * 1000
        t["persen_realisasi"] = round(t["realisasi"] / t["pagu_anggaran"] * 100, 2)

    elif anomaly_type == "round_number":
        # Nilai terlalu bulat (kelipatan 100jt persis) — indikasi manipulasi
        base = rng.choice([100_000_000, 200_000_000, 500_000_000, 1_000_000_000])
        t["realisasi"] = base
        t["pagu_anggaran"] = base + rng.choice([0, 50_000_000])
        t["persen_realisasi"] = round(t["realisasi"] / t["pagu_anggaran"] * 100, 2)

    elif anomaly_type == "benford_violation":
        # First digit yang tidak natural (banyak 8 dan 9)
        target_first = rng.choice([8, 9])
        magnitude = 10 ** rng.integers(7, 11)  # 10jt - 100M
        t["realisasi"] = int(target_first * magnitude + rng.integers(0, magnitude))
        t["realisasi"] = round(t["realisasi"] / 1000) * 1000
        t["pagu_anggaran"] = t["realisasi"] + rng.integers(1_000_000, 50_000_000)
        t["persen_realisasi"] = round(t["realisasi"] / t["pagu_anggaran"] * 100, 2)

    elif anomaly_type == "year_end_rushing":
        # Kontrak di minggu terakhir Desember — rushing anggaran
        year = t["tahun_anggaran"]
        day = rng.integers(20, 32)
        day = min(day, 31)
        t["tanggal_kontrak"] = f"{year}-12-{day:02d}"
        # Juga inflate nilai sedikit
        t["realisasi"] = round(t["realisasi"] * rng.uniform(1.1, 1.5) / 1000) * 1000
        t["persen_realisasi"] = round(t["realisasi"] / t["pagu_anggaran"] * 100, 2)

    elif anomaly_type == "markup":
        # Harga di-markup signifikan (pagu jauh di atas standar)
        t["pagu_anggaran"] = round(t["pagu_anggaran"] * rng.uniform(2.0, 5.0) / 1000) * 1000
        t["realisasi"] = round(t["pagu_anggaran"] * rng.uniform(0.90, 0.99) / 1000) * 1000
        t["persen_realisasi"] = round(t["realisasi"] / t["pagu_anggaran"] * 100, 2)

    return t


def generate_apbd_data(
    n_transactions: int = SYNTHETIC_NUM_TRANSACTIONS,
    anomaly_rate: float = SYNTHETIC_ANOMALY_RATE,
    seed: int = RANDOM_SEED,
    save: bool = True,
) -> pd.DataFrame:
    """
    Generate dataset APBD sintetis dengan anomali yang di-inject.

    Parameters
    ----------
    n_transactions : int
        Jumlah total transaksi.
    anomaly_rate : float
        Persentase transaksi anomali (0.0 - 1.0).
    seed : int
        Random seed untuk reproducibility.
    save : bool
        Simpan ke CSV di Silver layer.

    Returns
    -------
    pd.DataFrame
        DataFrame dengan semua transaksi + label ground truth.
    """
    rng = np.random.default_rng(seed)

    # Generate pool vendor
    n_vendors = 200
    vendor_pool = list(set([_generate_vendor_name(rng) for _ in range(n_vendors * 2)]))[:n_vendors]
    vendor_id_map = {v: f"VND-{i:04d}" for i, v in enumerate(vendor_pool)}

    n_anomaly = int(n_transactions * anomaly_rate)
    n_normal = n_transactions - n_anomaly

    anomaly_types = [
        "overbudget",
        "round_number",
        "benford_violation",
        "year_end_rushing",
        "markup",
    ]

    print(f"[DataGen] Generating {n_normal} normal + {n_anomaly} anomaly transactions...")

    # Generate normal transactions
    transactions = []
    for i in range(n_normal):
        t = _generate_normal_transaction(i, rng, vendor_pool, vendor_id_map)
        transactions.append(t)

    # Generate anomaly transactions
    for i in range(n_anomaly):
        t = _generate_normal_transaction(n_normal + i, rng, vendor_pool, vendor_id_map)
        atype = rng.choice(anomaly_types)
        t = _inject_anomaly(t, atype, rng)
        transactions.append(t)

    # Shuffle
    rng.shuffle(transactions)

    df = pd.DataFrame(transactions)

    # Reorder columns
    col_order = [
        "id_transaksi", "tahun_anggaran", "kota", "kode_skpd", "nama_skpd",
        "kode_rekening", "uraian_belanja", "pagu_anggaran", "realisasi",
        "persen_realisasi", "nama_vendor", "id_vendor", "tanggal_kontrak",
        "jenis_pengadaan", "is_anomaly_injected", "anomaly_type",
    ]
    df = df[col_order]

    if save:
        out_path = SILVER_DIR / "silver_apbd_belanja.csv"
        df.to_csv(out_path, index=False)
        print(f"[DataGen] Saved → {out_path}")
        print(f"[DataGen]   Total rows   : {len(df)}")
        print(f"[DataGen]   Anomalies    : {df['is_anomaly_injected'].sum()} ({anomaly_rate*100:.0f}%)")
        print(f"[DataGen]   Anomaly types: {df[df['is_anomaly_injected']]['anomaly_type'].value_counts().to_dict()}")

    return df


if __name__ == "__main__":
    df = generate_apbd_data()
    print("\n[DataGen] Sample data:")
    print(df.head(10).to_string())
    print(f"\n[DataGen] Dtypes:\n{df.dtypes}")
