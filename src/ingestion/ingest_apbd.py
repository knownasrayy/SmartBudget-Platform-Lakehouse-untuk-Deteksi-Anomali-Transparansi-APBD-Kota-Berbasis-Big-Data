"""
Adel - Data Ingestion Script (Milestone 2)
Sumber: APBD publik (Open Data Surabaya) + fallback simulasi realistis
Output: data/bronze/raw/apbd_surabaya_<YYYYMMDD>.csv
        data/bronze/raw/nlp_texts_<YYYYMMDD>.csv
"""

import requests
import pandas as pd
import os
import random
import logging
from datetime import datetime

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRONZE_RAW = os.path.join(BASE_DIR, "data", "bronze", "raw")
os.makedirs(BRONZE_RAW, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d")
KOTA      = "surabaya"

# ── 1. Coba ambil data real dari Open Data Surabaya ───────────────────────────
def fetch_apbd_opendata():
    log.info("Mencoba ambil data APBD dari Open Data Surabaya...")
    url = "https://opendata.surabaya.go.id/api/3/action/datastore_search"
    params = {"resource_id": "8a6a8a0a-3b3b-4b4b-8b8b-0b0b0b0b0b0b", "limit": 100}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("success") and data["result"]["records"]:
            df = pd.DataFrame(data["result"]["records"])
            log.info(f"Berhasil ambil {len(df)} baris dari Open Data Surabaya")
            return df
        raise ValueError("Data kosong atau endpoint tidak valid")
    except Exception as e:
        log.warning(f"Open Data Surabaya gagal: {e} → beralih ke fallback")
        return None

# ── 2. Fallback — generate data simulasi realistis ────────────────────────────
def generate_realistic_apbd():
    log.info("Generating data APBD realistis (fallback mode)...")
    random.seed(42)

    skpd_list = [
        "Dinas Pendidikan", "Dinas Kesehatan", "Dinas PU Bina Marga",
        "Dinas Perhubungan", "Dinas Sosial", "BPBD", "Dinas Lingkungan Hidup",
        "Sekretariat Daerah", "Dinas Kependudukan", "Dinas Pariwisata"
    ]
    jenis_belanja_list = [
        "Belanja Pegawai", "Belanja Barang & Jasa", "Belanja Modal",
        "Belanja Perjalanan Dinas", "Belanja Hibah"
    ]
    kegiatan_list = [
        "Pengadaan Alat Tulis Kantor", "Perjalanan Dinas Luar Negeri",
        "Pembangunan Gedung Kantor", "Rehabilitasi Jalan Lingkungan",
        "Pengadaan Kendaraan Dinas", "Pelatihan SDM Aparatur",
        "Pengadaan Seragam Pegawai", "Studi Banding ke Luar Daerah",
        "Pembangunan Drainase", "Pengadaan Peralatan Medis"
    ]
    kecamatan_list = [
        "Tambaksari", "Gubeng", "Rungkut", "Wonokromo", "Tenggilis Mejoyo",
        "Sukolilo", "Mulyorejo", "Bulak", "Kenjeran", "Semampir"
    ]

    rows = []
    for i in range(150):
        pagu = random.randint(50_000_000, 5_000_000_000)
        is_anomali = random.random() < 0.10
        if is_anomali:
            realisasi = int(pagu * random.uniform(1.4, 2.5))
            status = "ANOMALI"
        else:
            realisasi = int(pagu * random.uniform(0.6, 1.05))
            status = "NORMAL"

        rows.append({
            "id_transaksi"        : f"APBD-{KOTA.upper()}-2025-{i+1:04d}",
            "tanggal_scraping"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "kota"                : "Surabaya",
            "nama_skpd"           : random.choice(skpd_list),
            "kecamatan"           : random.choice(kecamatan_list),
            "jenis_belanja"       : random.choice(jenis_belanja_list),
            "nama_kegiatan"       : random.choice(kegiatan_list),
            "pagu_anggaran"       : pagu,
            "realisasi"           : realisasi,
            "selisih"             : realisasi - pagu,
            "persentase_realisasi": round(realisasi / pagu * 100, 2),
            "tahun_anggaran"      : 2025,
            "sumber_data"         : "Simulasi SIPD Surabaya 2025",
            "status"              : status,
        })

    df = pd.DataFrame(rows)
    log.info(f"Generated {len(df)} baris | Anomali: {df[df.status=='ANOMALI'].shape[0]} baris")
    return df

# ── 3. Data teks NLP (berita + tweet) ─────────────────────────────────────────
def generate_nlp_texts():
    log.info("Menyiapkan data teks NLP (berita + tweet)...")
    sample_texts = [
        {"id_transaksi": "TW-001", "sumber_data": "Twitter/X", "kota": "Surabaya",
         "teks": "Pipa PDAM di jalan MERR bocor lagi, air macet total sudah 3 hari. Laporan diabaikan terus! #Surabaya",
         "tanggal_scraping": "2025-09-10", "status": "RAW"},
        {"id_transaksi": "TW-002", "sumber_data": "Twitter/X", "kota": "Surabaya",
         "teks": "Anggaran perjalanan dinas Pemkot Surabaya 2025 naik 300%? Kemana transparansinya? #APBD #Korupsi",
         "tanggal_scraping": "2025-09-11", "status": "RAW"},
        {"id_transaksi": "TW-003", "sumber_data": "Twitter/X", "kota": "Surabaya",
         "teks": "Jalan Raya Darmo sudah diperbaiki, terima kasih Pemkot! Semoga tahan lama tidak seperti tahun lalu.",
         "tanggal_scraping": "2025-09-12", "status": "RAW"},
        {"id_transaksi": "TW-004", "sumber_data": "Twitter/X", "kota": "Surabaya",
         "teks": "Demo mahasiswa SPM-MP soal APBD Surabaya 2025 janggal. Ratusan miliar entah kemana.",
         "tanggal_scraping": "2025-09-13", "status": "RAW"},
        {"id_transaksi": "TW-005", "sumber_data": "Twitter/X", "kota": "Surabaya",
         "teks": "Pelayanan Dispendukcapil Surabaya makin bagus, antrian online sangat membantu warga.",
         "tanggal_scraping": "2025-09-14", "status": "RAW"},
        {"id_transaksi": "NEWS-001", "sumber_data": "Berita", "kota": "Surabaya",
         "teks": "KPK mengendus dugaan markup anggaran belanja modal Dinas PU Surabaya senilai Rp 200 miliar.",
         "tanggal_scraping": "2025-09-15", "status": "RAW"},
        {"id_transaksi": "NEWS-002", "sumber_data": "Berita", "kota": "Surabaya",
         "teks": "Pemkot Surabaya raih penghargaan Smart City terbaik dari Kemendagri untuk kategori tata kelola digital.",
         "tanggal_scraping": "2025-09-16", "status": "RAW"},
        {"id_transaksi": "NEWS-003", "sumber_data": "Berita", "kota": "Surabaya",
         "teks": "Warga Kenjeran keluhkan banjir rob yang makin parah, drainase tidak kunjung diperbaiki.",
         "tanggal_scraping": "2025-09-17", "status": "RAW"},
        {"id_transaksi": "NEWS-004", "sumber_data": "Berita", "kota": "Surabaya",
         "teks": "BPK menemukan 47 temuan ketidaksesuaian dalam laporan keuangan APBD Surabaya 2024.",
         "tanggal_scraping": "2025-09-18", "status": "RAW"},
        {"id_transaksi": "NEWS-005", "sumber_data": "Berita", "kota": "Surabaya",
         "teks": "Program beasiswa Pemkot Surabaya disambut antusias warga, 5000 pelajar mendaftar.",
         "tanggal_scraping": "2025-09-19", "status": "RAW"},
    ]
    df = pd.DataFrame(sample_texts)
    log.info(f"Loaded {len(df)} teks NLP")
    return df

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 50)
    log.info("SmartBudget — Data Ingestion Pipeline (Adel)")
    log.info("=" * 50)

    # — APBD —
    df_apbd = fetch_apbd_opendata()
    if df_apbd is None:
        df_apbd = generate_realistic_apbd()

    out_apbd = os.path.join(BRONZE_RAW, f"apbd_{KOTA}_{TIMESTAMP}.csv")
    df_apbd.to_csv(out_apbd, index=False, encoding="utf-8-sig")
    log.info(f"Saved APBD → {out_apbd}")

    # — NLP texts —
    df_nlp = generate_nlp_texts()
    out_nlp = os.path.join(BRONZE_RAW, f"nlp_texts_{KOTA}_{TIMESTAMP}.csv")
    df_nlp.to_csv(out_nlp, index=False, encoding="utf-8-sig")
    log.info(f"Saved NLP  → {out_nlp}")

    log.info("=" * 50)
    log.info(f"✅ Ingestion selesai! Total APBD: {len(df_apbd)} baris | NLP: {len(df_nlp)} baris")
    log.info(f"📁 Output folder: {BRONZE_RAW}")
    log.info("=" * 50)