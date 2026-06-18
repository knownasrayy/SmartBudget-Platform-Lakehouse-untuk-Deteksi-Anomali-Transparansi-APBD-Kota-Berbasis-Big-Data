"""
process_lpse_silver.py
========================
Memproses data mentah LPSE (Tender & Vendor) dari folder Bronze,
melakukan pembersihan, dan menyimpannya ke folder Silver.
Data ini akan menggantikan data vendor sintetis.
"""

import pandas as pd
import numpy as np
import os
import glob
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ml_engine.config import BRONZE_DIR, SILVER_DIR

# Pastikan import generator properties dari generate_vendor_network untuk mengisi kolom wajib
from ml_engine.data_generator.generate_vendor_network import (
    _generate_alamat, _generate_nama_direktur, _generate_npwp
)

def process_lpse_data():
    print("[Silver] Memproses data LPSE/Vendor dari Bronze Layer...")
    
    # Cari file LPSE terbaru di Bronze
    lpse_files = glob.glob(os.path.join(BRONZE_DIR, "lpse_raw_*.csv"))
    if not lpse_files:
        print("[Silver] [WARNING] File lpse_raw_*.csv tidak ditemukan di Bronze. Harap jalankan ingestion LPSE dulu.")
        return None, None
        
    latest_lpse_file = max(lpse_files, key=os.path.getctime)
    print(f"[Silver] Membaca file: {os.path.basename(latest_lpse_file)}")
    
    df_raw = pd.read_csv(latest_lpse_file)
    
    # 1. Cleaning & Formating Data Tender
    df_tender = df_raw.copy()
    
    # Pastikan numerik
    for col in ['nilai_pagu', 'nilai_hps', 'nilai_kontrak']:
        if col in df_tender.columns:
            df_tender[col] = pd.to_numeric(df_tender[col], errors='coerce').fillna(0.0)
            
    # Buat nilai kontrak jika tidak ada (untuk data scraped yang belum ada nilai kontrak akhir)
    if 'nilai_kontrak' not in df_tender.columns:
        df_tender['nilai_kontrak'] = df_tender['nilai_hps'] * np.random.uniform(0.8, 0.98, size=len(df_tender))
        
    out_tender_path = os.path.join(SILVER_DIR, "silver_lpse_tender.csv")
    df_tender.to_csv(out_tender_path, index=False)
    print(f"  → Tersimpan: {out_tender_path} ({len(df_tender)} tender)")
    
    # 2. Aggregasi Data Vendor
    print("[Silver] Mengagregasi profil vendor dari riwayat tender...")
    df_vendor_agg = df_tender.groupby('nama_vendor').agg(
        total_kontrak=('id_tender', 'count'),
        total_nilai_kontrak=('nilai_kontrak', 'sum')
    ).reset_index()
    
    # Beri ID Vendor & Property Lengkap (sebagian di-generate untuk melengkapi skema pipeline yang butuh fitur graf)
    rng = np.random.default_rng(42)
    vendors = []
    
    for idx, row in df_vendor_agg.iterrows():
        # Buat label fraud jika vendor menang banyak tender (untuk keperluan deteksi)
        is_fraud = row['total_kontrak'] > 15 or row['total_nilai_kontrak'] > 10_000_000_000
        fraud_type = "monopoly_risk" if is_fraud else "none"
        
        vendors.append({
            "id_vendor": f"VND-{idx:04d}",
            "nama_vendor": row['nama_vendor'],
            "alamat": _generate_alamat(rng),  # Idealnya dari Inaproc API, pakai mock dulu
            "no_telp": f"031-{rng.integers(1000000, 9999999)}",
            "nama_direktur": _generate_nama_direktur(rng),
            "npwp": _generate_npwp(rng),
            "tahun_berdiri": int(rng.integers(1990, 2024)),
            "total_kontrak": int(row['total_kontrak']),
            "total_nilai_kontrak": float(row['total_nilai_kontrak']),
            "is_fraud_vendor": is_fraud,
            "fraud_type": fraud_type,
        })
        
    df_vendors = pd.DataFrame(vendors)
    
    # Tambahkan sedikit Shell Companies untuk Graph Analysis (alamat/direktur sama)
    # Ambil 2 alamat dari 2 vendor pertama dan set ke 2 vendor berikutnya
    if len(df_vendors) >= 4:
        df_vendors.at[2, 'alamat'] = df_vendors.at[0, 'alamat']
        df_vendors.at[2, 'is_fraud_vendor'] = True
        df_vendors.at[2, 'fraud_type'] = "shell_company_address"
        
        df_vendors.at[3, 'nama_direktur'] = df_vendors.at[1, 'nama_direktur']
        df_vendors.at[3, 'is_fraud_vendor'] = True
        df_vendors.at[3, 'fraud_type'] = "shell_company_director"
    
    out_vendor_path = os.path.join(SILVER_DIR, "silver_vendor_network.csv")
    df_vendors.to_csv(out_vendor_path, index=False)
    print(f"  → Tersimpan: {out_vendor_path} ({len(df_vendors)} vendor)")
    
    return df_tender, df_vendors

if __name__ == "__main__":
    process_lpse_data()
