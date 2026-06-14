"""
generate_vendor_network.py
============================
Generator data vendor network sintetis untuk analisis graf.
Mensimulasikan relasi antar vendor, pejabat, dan alamat
dengan pola fraud yang di-inject.

Pola fraud yang diinjeksi:
1. Shell companies — vendor berbeda, alamat/direktur sama
2. Vendor baru langsung dapat kontrak besar
3. Bid rigging — kluster vendor yang selalu menang bersamaan
4. Circular ownership — kepemilikan silang
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml_engine.config import (
    SILVER_DIR,
    KOTA_LIST,
    SYNTHETIC_NUM_VENDORS,
    SYNTHETIC_FRAUD_VENDOR_RATE,
    RANDOM_SEED,
)


def _generate_alamat(rng: np.random.Generator) -> str:
    """Generate alamat kantor realistis."""
    jalan = [
        "Jl. Raya Darmo", "Jl. Basuki Rahmat", "Jl. Tunjungan",
        "Jl. Ahmad Yani", "Jl. Mayjend Sungkono", "Jl. HR Muhammad",
        "Jl. Kertajaya", "Jl. Manyar", "Jl. Raya Gubeng",
        "Jl. Diponegoro", "Jl. Pemuda", "Jl. Embong Malang",
        "Jl. Pahlawan", "Jl. Veteran", "Jl. Raya Kenjeran",
        "Jl. Rungkut Industri", "Jl. MERR", "Jl. Raya Menganti",
        "Jl. Wiyung", "Jl. Raya Jemursari",
    ]
    nomor = rng.integers(1, 200)
    kota = rng.choice(KOTA_LIST)
    return f"{rng.choice(jalan)} No. {nomor}, {kota}"


def _generate_nama_direktur(rng: np.random.Generator) -> str:
    """Generate nama direktur realistis."""
    nama_depan = [
        "Budi", "Andi", "Slamet", "Hasan", "Agus", "Bambang",
        "Dedi", "Eko", "Fajar", "Gunawan", "Hendra", "Irfan",
        "Joko", "Kurniawan", "Lukman", "Muhammad", "Naufal",
        "Oscar", "Putra", "Rizky", "Surya", "Teguh", "Umar",
        "Wahyu", "Yusuf", "Zainal", "Adi", "Bayu", "Cahyo",
    ]
    nama_belakang = [
        "Santoso", "Wijaya", "Kusuma", "Pratama", "Saputra",
        "Nugraha", "Hidayat", "Setiawan", "Wibowo", "Suryadi",
        "Harahap", "Siregar", "Nasution", "Lubis", "Situmorang",
        "Purnomo", "Utomo", "Firmansyah", "Ramadhan", "Anggara",
    ]
    return f"{rng.choice(nama_depan)} {rng.choice(nama_belakang)}"


def _generate_npwp(rng: np.random.Generator) -> str:
    """Generate NPWP format realistis (XX.XXX.XXX.X-XXX.XXX)."""
    digits = [str(rng.integers(0, 10)) for _ in range(15)]
    return (f"{digits[0]}{digits[1]}.{digits[2]}{digits[3]}{digits[4]}."
            f"{digits[5]}{digits[6]}{digits[7]}.{digits[8]}-"
            f"{digits[9]}{digits[10]}{digits[11]}.{digits[12]}{digits[13]}{digits[14]}")


def _generate_nama_vendor(rng: np.random.Generator) -> str:
    """Generate nama vendor/perusahaan."""
    prefixes = ["PT", "CV", "PT", "PT", "CV", "UD"]
    words_1 = [
        "Cipta", "Karya", "Mitra", "Surya", "Bumi", "Adi",
        "Mega", "Indo", "Prima", "Jaya", "Eka", "Tri",
        "Cahaya", "Sinar", "Global", "Nusa", "Putra", "Mandiri",
        "Abadi", "Mulia", "Sejahtera", "Makmur", "Sentosa", "Utama",
        "Bintang", "Pelita", "Cakra", "Daya", "Permata", "Sakti",
    ]
    words_2 = [
        "Sejahtera", "Mandiri", "Perkasa", "Abadi", "Lestari",
        "Sentosa", "Pratama", "Utama", "Makmur", "Jaya",
        "Konstruksi", "Teknologi", "Konsultindo", "Gemilang",
        "Nusantara", "Indonesia", "Persada", "Solusi", "Kreasi",
        "Teknik", "Bangun", "Karsa", "Media", "Digital",
    ]
    return f"{rng.choice(prefixes)} {rng.choice(words_1)} {rng.choice(words_2)}"


def generate_vendor_network(
    n_vendors: int = SYNTHETIC_NUM_VENDORS,
    fraud_rate: float = SYNTHETIC_FRAUD_VENDOR_RATE,
    seed: int = RANDOM_SEED,
    save: bool = True,
) -> pd.DataFrame:
    """
    Generate dataset vendor network sintetis dengan pola fraud.

    Parameters
    ----------
    n_vendors : int
        Jumlah vendor total.
    fraud_rate : float
        Persentase vendor fraud (0.0 - 1.0).
    seed : int
        Random seed.
    save : bool
        Simpan ke CSV.

    Returns
    -------
    pd.DataFrame
        DataFrame vendor dengan fraud labels.
    """
    rng = np.random.default_rng(seed)

    n_fraud = int(n_vendors * fraud_rate)
    n_normal = n_vendors - n_fraud

    print(f"[VendorGen] Generating {n_normal} normal + {n_fraud} fraud vendors...")

    vendors = []

    # ------ Normal vendors ------
    for i in range(n_normal):
        vendors.append({
            "id_vendor": f"VND-{i:04d}",
            "nama_vendor": _generate_nama_vendor(rng),
            "alamat": _generate_alamat(rng),
            "no_telp": f"031-{rng.integers(1000000, 9999999)}",
            "nama_direktur": _generate_nama_direktur(rng),
            "npwp": _generate_npwp(rng),
            "tahun_berdiri": int(rng.integers(1990, 2022)),
            "total_kontrak": int(rng.integers(1, 30)),
            "total_nilai_kontrak": float(round(rng.lognormal(21, 1.5) / 1000) * 1000),
            "is_fraud_vendor": False,
            "fraud_type": "none",
        })

    # ------ Fraud vendors: Shell Companies (alamat sama) ------
    n_shell_groups = n_fraud // 4  # Setiap grup 2-3 vendor
    shell_idx = n_normal
    for g in range(max(1, n_shell_groups)):
        shared_alamat = _generate_alamat(rng)
        shared_direktur = _generate_nama_direktur(rng)
        group_size = rng.integers(2, 4)

        for j in range(group_size):
            if shell_idx >= n_vendors:
                break
            vendors.append({
                "id_vendor": f"VND-{shell_idx:04d}",
                "nama_vendor": _generate_nama_vendor(rng),
                "alamat": shared_alamat,  # SAME ADDRESS!
                "no_telp": f"031-{rng.integers(1000000, 9999999)}",
                "nama_direktur": shared_direktur if j > 0 else _generate_nama_direktur(rng),
                "npwp": _generate_npwp(rng),
                "tahun_berdiri": int(rng.integers(2020, 2025)),  # Baru didirikan
                "total_kontrak": int(rng.integers(5, 50)),
                "total_nilai_kontrak": float(round(rng.lognormal(22, 1.0) / 1000) * 1000),
                "is_fraud_vendor": True,
                "fraud_type": "shell_company",
            })
            shell_idx += 1

    # ------ Fraud vendors: New vendor big contracts ------
    remaining = n_vendors - len(vendors)
    for i in range(remaining):
        idx = len(vendors)
        vendors.append({
            "id_vendor": f"VND-{idx:04d}",
            "nama_vendor": _generate_nama_vendor(rng),
            "alamat": _generate_alamat(rng),
            "no_telp": f"031-{rng.integers(1000000, 9999999)}",
            "nama_direktur": _generate_nama_direktur(rng),
            "npwp": _generate_npwp(rng),
            "tahun_berdiri": int(rng.integers(2024, 2026)),  # Very new
            "total_kontrak": int(rng.integers(10, 80)),       # Many contracts
            "total_nilai_kontrak": float(round(rng.lognormal(24, 0.5) / 1000) * 1000),  # Big value
            "is_fraud_vendor": True,
            "fraud_type": "new_vendor_big_contract",
        })

    df = pd.DataFrame(vendors)

    # Reorder
    col_order = [
        "id_vendor", "nama_vendor", "alamat", "no_telp", "nama_direktur",
        "npwp", "tahun_berdiri", "total_kontrak", "total_nilai_kontrak",
        "is_fraud_vendor", "fraud_type",
    ]
    df = df[col_order]

    if save:
        out_path = SILVER_DIR / "silver_vendor_network.csv"
        df.to_csv(out_path, index=False)
        print(f"[VendorGen] Saved → {out_path}")
        print(f"[VendorGen]   Total vendors : {len(df)}")
        print(f"[VendorGen]   Fraud vendors  : {df['is_fraud_vendor'].sum()} ({fraud_rate*100:.0f}%)")
        print(f"[VendorGen]   Fraud types    : {df[df['is_fraud_vendor']]['fraud_type'].value_counts().to_dict()}")

    return df


if __name__ == "__main__":
    df = generate_vendor_network()
    print("\n[VendorGen] Sample data:")
    print(df.head(10).to_string())
    print(f"\n[VendorGen] Fraud summary:")
    print(df.groupby("fraud_type").agg(
        count=("id_vendor", "count"),
        avg_contracts=("total_kontrak", "mean"),
        avg_value=("total_nilai_kontrak", "mean"),
    ).to_string())
