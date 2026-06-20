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
    print("[1/2] Mengambil SEMUA data APBD dari Open Data Surabaya (2023-2026)...")
    dataset_url = "https://ckan.surabaya.go.id/api/3/action/package_show?id=6bcf082f-6ee8-44e3-8ab5-d85f7d43ba71"
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get all resources in the dataset
        resp = requests.get(dataset_url, verify=False, timeout=20)
        dataset_data = resp.json()
        if not dataset_data.get("success"):
            raise ValueError("Gagal mendapatkan dataset CKAN")
            
        resources = dataset_data["result"]["resources"]
        print(f"   -> Ditemukan {len(resources)} tabel (resources) di CKAN.")
        
        mapped_rows = []
        import random
        random.seed(42)
        kecamatan_list = ["Tambaksari", "Gubeng", "Rungkut", "Wonokromo", "Tenggilis Mejoyo", "Sukolilo", "Mulyorejo", "Bulak", "Kenjeran", "Semampir"]
        
        row_id_counter = 1
        
        for res in resources:
            res_id = res["id"]
            res_name = res.get("name", "Unknown")
            print(f"      Mengambil data dari: {res_name} ({res_id})")
            
            search_url = f"https://ckan.surabaya.go.id/api/3/action/datastore_search?resource_id={res_id}&limit=1000"
            search_resp = requests.get(search_url, verify=False, timeout=20)
            search_data = search_resp.json()
            
            if search_data.get("success") and search_data["result"]["records"]:
                records = search_data["result"]["records"]
                
                # Extract year/month context if possible from created date
                created_date = res.get("created", "2024-01-01")[:10]
                year_context = int(created_date[:4])
                
                for row in records:
                    def safe_float(v):
                        if not v or v == "-": return 0.0
                        try: return float(v)
                        except: return 0.0
                        
                    anggaran = safe_float(row.get("target_pendapatan_berdasarkan_apbd", 0))
                    realisasi = safe_float(row.get("realisasi_apbd", 0))
                    if anggaran == 0 and realisasi == 0:
                        continue # Skip empty rows
                        
                    selisih = realisasi - anggaran
                    persen = (realisasi / anggaran * 100) if anggaran > 0 else 0.0
                    
                    mapped_rows.append({
                        "id": f"APBD-REAL-{row_id_counter:05d}",
                        "tahun": year_context,
                        "skpd": row.get("pd_penghasil", "Tidak Diketahui"),
                        "kecamatan": random.choice(kecamatan_list), # Dummy utk heatmap mapping
                        "kategori_belanja": row.get("jenis_pendapatan_daerah_per_sektor", "Lainnya"),
                        "anggaran": anggaran,
                        "realisasi": realisasi,
                        "selisih": selisih,
                        "persen_realisasi": round(persen, 2),
                        "tanggal_input": created_date,
                        "sumber": "Open Data Surabaya (CKAN API)"
                    })
                    row_id_counter += 1
        
        if mapped_rows:
            df = pd.DataFrame(mapped_rows)
            print(f"   [OK] Total data asli berhasil ditarik: {len(df)} baris dari seluruh periode!")
            return df
        else:
            raise ValueError("Semua resource kosong")
            
    except Exception as e:
        print(f"   [X] Gagal: {e}")
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
    print(f"   [OK] Generated {len(df)} baris data APBD realistis")
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
    print(f"   [OK] Loaded {len(df)} sample teks untuk NLP pipeline")
    return df

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SmartBudget — Data Ingestion (Adel)")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # APBD data
    df_apbd = fetch_apbd_opendata()
    if df_apbd is None:
        df_apbd = generate_realistic_apbd()

    out_apbd = os.path.join(BRONZE_DIR, f"apbd_surabaya_raw_{timestamp_str}.csv")
    df_apbd.to_csv(out_apbd, index=False, encoding="utf-8-sig")
    print(f"\n   -> Saved: {out_apbd}")

    # News/tweet data
    df_news = fetch_news_headlines()
    out_news = os.path.join(BRONZE_DIR, f"tweets_berita_raw_{timestamp_str}.csv")
    df_news.to_csv(out_news, index=False, encoding="utf-8-sig")
    print(f"   -> Saved: {out_news}")

    print("\n" + "=" * 55)
    print("  ✅ Ingestion selesai! Cek folder data/bronze/")
    print("=" * 55)

    # Preview
    print("\nPreview APBD (5 baris pertama):")
    print(df_apbd.head())
    print(f"\nTotal baris APBD  : {len(df_apbd)}")
    print(f"Total baris NLP   : {len(df_news)}")
    print(f"Anomali terdeteksi: {len(df_apbd[df_apbd['persen_realisasi'] > 130])} baris (realisasi > 130% anggaran)")