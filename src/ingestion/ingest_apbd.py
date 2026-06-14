"""
Adel - Data Ingestion Script
Sumber: Dataset APBD publik via requests + BeautifulSoup
Output: data/bronze/apbd_surabaya_raw.csv
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# ── Path output ke bronze layer ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")
os.makedirs(BRONZE_DIR, exist_ok=True)

# ── 1. Ambil data APBD dari Open Data Surabaya ───────────────────────────────
def fetch_apbd_opendata():
    print("[1/2] Mengambil data APBD dari Open Data Surabaya...")
    url = "https://opendata.surabaya.go.id/api/3/action/datastore_search"
    params = {
        "resource_id": "8a6a8a0a-3b3b-4b4b-8b8b-0b0b0b0b0b0b",  # akan di-replace
        "limit": 100
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("success") and data["result"]["records"]:
            df = pd.DataFrame(data["result"]["records"])
            print(f"   ✓ Berhasil ambil {len(df)} baris dari Open Data Surabaya")
            return df
        else:
            raise ValueError("Data kosong atau endpoint berubah")
    except Exception as e:
        print(f"   ✗ Gagal: {e}")
        return None

# ── 2. Fallback — simulasi data realistis APBD Surabaya ──────────────────────
def generate_realistic_apbd():
    print("[1/2] Generating data APBD realistis (fallback)...")
    
    import random
    random.seed(42)

    skpd_list = [
        "Dinas Pendidikan", "Dinas Kesehatan", "Dinas PU Bina Marga",
        "Dinas Perhubungan", "Dinas Sosial", "BPBD", "Dinas Lingkungan Hidup",
        "Sekretariat Daerah", "Dinas Kependudukan", "Dinas Pariwisata"
    ]
    kategori_list = [
        "Belanja Pegawai", "Belanja Barang & Jasa", "Belanja Modal",
        "Belanja Perjalanan Dinas", "Belanja Hibah"
    ]
    kecamatan_list = [
        "Tambaksari", "Gubeng", "Rungkut", "Wonokromo", "Tenggilis Mejoyo",
        "Sukolilo", "Mulyorejo", "Bulak", "Kenjeran", "Semampir"
    ]

    rows = []
    for i in range(150):
        anggaran = random.randint(50_000_000, 5_000_000_000)
        # Sisipkan 10% anomali (nilai ekstrem)
        if random.random() < 0.10:
            realisasi = int(anggaran * random.uniform(1.4, 2.5))  # markup janggal
        else:
            realisasi = int(anggaran * random.uniform(0.6, 1.05))

        rows.append({
            "id": f"APBD-2025-{i+1:04d}",
            "tahun": 2025,
            "skpd": random.choice(skpd_list),
            "kecamatan": random.choice(kecamatan_list),
            "kategori_belanja": random.choice(kategori_list),
            "anggaran": anggaran,
            "realisasi": realisasi,
            "selisih": realisasi - anggaran,
            "persen_realisasi": round(realisasi / anggaran * 100, 2),
            "tanggal_input": f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "sumber": "Simulasi SIPD Surabaya 2025"
        })

    df = pd.DataFrame(rows)
    print(f"   ✓ Generated {len(df)} baris data APBD realistis")
    return df

# ── 3. Ambil berita via NewsAPI (opsional, butuh API key) ────────────────────
def fetch_news_headlines():
    print("[2/2] Mengambil sample teks berita/tweet untuk NLP...")

    # Sample teks manual — realistis dari konteks Surabaya
    sample_texts = [
        {"id": "TW-001", "sumber": "Twitter/X", "teks": "Pipa PDAM di jalan MERR bocor lagi, air macet total sudah 3 hari. Laporan diabaikan terus! #Surabaya", "tanggal": "2025-09-10"},
        {"id": "TW-002", "sumber": "Twitter/X", "teks": "Anggaran perjalanan dinas Pemkot Surabaya 2025 naik 300%? Kemana transparansinya? #APBD #Korupsi", "tanggal": "2025-09-11"},
        {"id": "TW-003", "sumber": "Twitter/X", "teks": "Jalan Raya Darmo sudah diperbaiki, terima kasih Pemkot! Semoga tahan lama tidak seperti tahun lalu.", "tanggal": "2025-09-12"},
        {"id": "TW-004", "sumber": "Twitter/X", "teks": "Demo mahasiswa SPM-MP soal APBD Surabaya 2025 janggal. Ratusan miliar entah kemana.", "tanggal": "2025-09-13"},
        {"id": "TW-005", "sumber": "Twitter/X", "teks": "Pelayanan Dispendukcapil Surabaya makin bagus, antrian online sangat membantu warga.", "tanggal": "2025-09-14"},
        {"id": "NEWS-001", "sumber": "Berita", "teks": "KPK mengendus dugaan markup anggaran belanja modal Dinas PU Surabaya senilai Rp 200 miliar.", "tanggal": "2025-09-15"},
        {"id": "NEWS-002", "sumber": "Berita", "teks": "Pemkot Surabaya raih penghargaan Smart City terbaik dari Kemendagri untuk kategori tata kelola digital.", "tanggal": "2025-09-16"},
        {"id": "NEWS-003", "sumber": "Berita", "teks": "Warga Kenjeran keluhkan banjir rob yang makin parah, drainase tidak kunjung diperbaiki.", "tanggal": "2025-09-17"},
        {"id": "NEWS-004", "sumber": "Berita", "teks": "BPK menemukan 47 temuan ketidaksesuaian dalam laporan keuangan APBD Surabaya 2024.", "tanggal": "2025-09-18"},
        {"id": "NEWS-005", "sumber": "Berita", "teks": "Program beasiswa Pemkot Surabaya disambut antusias warga, 5000 pelajar mendaftar.", "tanggal": "2025-09-19"},
    ]

    df = pd.DataFrame(sample_texts)
    print(f"   ✓ Loaded {len(df)} sample teks untuk NLP pipeline")
    return df

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SmartBudget — Data Ingestion (Adel)")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # APBD data
    df_apbd = fetch_apbd_opendata()
    if df_apbd is None:
        df_apbd = generate_realistic_apbd()

    out_apbd = os.path.join(BRONZE_DIR, "apbd_surabaya_raw.csv")
    df_apbd.to_csv(out_apbd, index=False, encoding="utf-8-sig")
    print(f"\n   → Saved: {out_apbd}")

    # News/tweet data
    df_news = fetch_news_headlines()
    out_news = os.path.join(BRONZE_DIR, "tweets_berita_raw.csv")
    df_news.to_csv(out_news, index=False, encoding="utf-8-sig")
    print(f"   → Saved: {out_news}")

    print("\n" + "=" * 55)
    print("  ✅ Ingestion selesai! Cek folder data/bronze/")
    print("=" * 55)

    # Preview
    print("\nPreview APBD (5 baris pertama):")
    print(df_apbd.head())
    print(f"\nTotal baris APBD  : {len(df_apbd)}")
    print(f"Total baris NLP   : {len(df_news)}")
    print(f"Anomali terdeteksi: {len(df_apbd[df_apbd['persen_realisasi'] > 130])} baris (realisasi > 130% anggaran)")