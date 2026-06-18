import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
BRONZE_DIR = BASE_DIR / "data/bronze"

def generate_mock_social_data(num_records=50):
    print(f"[Ingestion] Generating {num_records} mock news & social media records...")
    
    platforms = ['Twitter/X', 'Portal Berita', 'Instagram', 'Layanan Aduan Warga', 'Facebook']
    sources = {
        'Twitter/X': ['@wargasurabaya', '@mahasiswait', '@pemantaukota', '@surabayakita', '@budi_utomo'],
        'Portal Berita': ['Detik Jatim', 'Kompas', 'Suara Surabaya', 'Radar Surabaya'],
        'Instagram': ['@aslisuroboyo', '@surabayaterkini', '@lovesurabaya'],
        'Layanan Aduan Warga': ['Wargaku', 'Lapor!'],
        'Facebook': ['Grup Suara Warga Surabaya', 'Info Lantas Surabaya']
    }
    
    # Kumpulan template kalimat agar realistis (Fokus ke APBD Surabaya / korupsi / fasilitas)
    teks_positif = [
        "Pembangunan RTH di pinggiran kota sangat bagus. Anggaran tahun ini benar-benar terasa manfaatnya.",
        "Terima kasih Pemkot Surabaya! Jalanan di area industri SIER sudah mulus kembali.",
        "Pelayanan RSUD semakin cepat setelah ada penambahan alokasi dana kesehatan di APBD.",
        "Beasiswa pemuda berprestasi sudah cair, transparansi dana pendidikan patut diacungi jempol.",
        "Lampu penerangan jalan umum (PJU) sudah diperbaiki semua di wilayah Kenjeran."
    ]
    
    teks_negatif = [
        "Janggal sekali! Anggaran perjalanan dinas dewan naik drastis tapi fasilitas sekolah masih kurang.",
        "Ada indikasi mark-up proyek gorong-gorong di Wonokromo. KPK tolong audit APBD ini!",
        "Proyek taman mangkrak dari tahun lalu, kemana larinya sisa anggaran? #KorupsiProyek",
        "Masih banyak jalan berlubang di pinggiran, padahal klaim anggaran perbaikan jalan sangat besar.",
        "Lelang proyek sepertinya dimonopoli vendor tertentu. Transparansi LPSE patut dipertanyakan."
    ]
    
    teks_netral = [
        "Sidang paripurna APBD 2025 Kota Surabaya akan diselenggarakan minggu depan.",
        "Pemkot berencana mengalihkan sebagian dana infrastruktur untuk penanganan banjir tahun ini.",
        "Warga berharap ada porsi anggaran yang lebih besar untuk UMKM di tahun depan.",
        "Rincian alokasi belanja daerah dapat dilihat di website resmi SIPD.",
        "Diskusi publik tentang efisiensi APBD digelar oleh mahasiswa ITS hari ini."
    ]
    
    records = []
    end_date = datetime.now()
    
    for _ in range(num_records):
        platform = random.choices(platforms, weights=[40, 20, 20, 10, 10])[0]
        sumber = random.choice(sources[platform])
        
        # Determine sentiment type to pick text
        sentiment_type = random.choices(["Positif", "Negatif", "Netral"], weights=[30, 40, 30])[0]
        
        if sentiment_type == "Positif":
            teks = random.choice(teks_positif)
        elif sentiment_type == "Negatif":
            teks = random.choice(teks_negatif)
        else:
            teks = random.choice(teks_netral)
            
        # Randomize date within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        mins_ago = random.randint(0, 59)
        dt = end_date - timedelta(days=days_ago, hours=hours_ago, minutes=mins_ago)
        tanggal_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        records.append({
            "tanggal": tanggal_str,
            "platform": platform,
            "sumber": sumber,
            "teks": teks
        })
        
    df = pd.DataFrame(records)
    
    # Urutkan berdasarkan tanggal terbaru
    df = df.sort_values(by="tanggal", ascending=False)
    
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = BRONZE_DIR / f"tweets_berita_raw_{timestamp}.csv"
    
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"[Ingestion] Selesai! Data disimpan ke: {out_file}")
    print(df.head())

if __name__ == "__main__":
    generate_mock_social_data(200)
