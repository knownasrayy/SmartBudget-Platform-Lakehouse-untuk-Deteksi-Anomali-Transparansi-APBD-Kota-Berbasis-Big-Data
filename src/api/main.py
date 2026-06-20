import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="SmartBudget Lakehouse API")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Paths
BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "gold"
DASHBOARD_DIR = BASE_DIR / "src" / "dashboard"

# Helper function to read CSV and convert to dict list
def read_csv_to_dict(filename):
    file_path = GOLD_DIR / filename
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []
    try:
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        df = df.fillna("")
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

@app.get("/api/summary")
def get_summary():
    """Mengembalikan ringkasan anggaran SKPD (KPI 1)"""
    data = read_csv_to_dict("gold_skpd_summary.csv")
    return JSONResponse(content=data)

def safe_float(val):
    try:
        if val == "": return 0.0
        return float(val)
    except:
        return 0.0

@app.get("/api/anomalies")
def get_anomalies():
    """Mengembalikan SEMUA data transaksi untuk Time-Series & Tabel (KPI 2)"""
    # Membaca seluruh data yang sudah di-skoring (bukan hanya yang anomali)
    data = read_csv_to_dict("gold_anomaly_transactions.csv")
    
    if not data:
        return JSONResponse(content=[])
        
    # Urutkan berdasarkan anomaly_score dari terbesar agar yang anomali di atas
    data = sorted(data, key=lambda x: safe_float(x.get('anomaly_score', 0)), reverse=True)
    
    # Map kolom agar terbaca oleh main.js frontend
    for row in data:
        row['id_transaksi'] = row.get('id', '')
        
        # is_anomaly berasal asli dari Spark MLlib
        if row.get('is_anomaly') == 1 or row.get('is_anomaly') == '1':
            row['is_flagged'] = '1'
            row['anomaly_label'] = 'Anomali'
        else:
            row['is_flagged'] = '0'
            row['anomaly_label'] = 'Normal'
            
        uraian = row.get('kategori_belanja', '')
        # Fix typo from dummy generator
        uraian = uraian.replace('Pengadaan Pengadaan', 'Pengadaan')
        row['uraian_belanja'] = uraian
        
        # Populate jenis_pengadaan if empty
        if not row.get('jenis_pengadaan') or row.get('jenis_pengadaan') == '-':
            if 'Konstruksi' in uraian: row['jenis_pengadaan'] = 'Pekerjaan Konstruksi'
            elif 'Konsultansi' in uraian: row['jenis_pengadaan'] = 'Jasa Konsultansi'
            elif 'Barang' in uraian: row['jenis_pengadaan'] = 'Pengadaan Barang'
            else: row['jenis_pengadaan'] = 'Jasa Lainnya'

        row['zscore_per_rekening'] = row.get('anomaly_score', 0)
        
        # Ekstrak bulan dari tanggal_input
        # Format tanggal_input: YYYY-MM-DDT... atau YYYY-MM-DD
        tgl = str(row.get('tanggal_input', ''))
        bulan = "1"
        if len(tgl) >= 7 and tgl[4] == '-':
            try: bulan = str(int(tgl[5:7]))
            except: pass
        row['bulan_kontrak'] = bulan

    return JSONResponse(content=data)

@app.get("/api/sentiment")
def get_sentiment():
    """Mengembalikan hasil analisis sentimen opini publik (KPI 3)"""
    data = read_csv_to_dict("sentiment_results.csv")
    # Jika gagal dibaca karena error utf-8, coba dengan windows-1252
    if not data:
        file_path = GOLD_DIR / "sentiment_results.csv"
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, encoding='windows-1252', on_bad_lines='skip')
                df = df.fillna("")
                data = df.to_dict(orient='records')
            except Exception as e:
                print(f"Error fallback read sentiment: {e}")
    return JSONResponse(content=data)

@app.get("/api/vendors")
def get_vendors():
    """Mengembalikan daftar jejaring vendor pengadaan"""
    data = read_csv_to_dict("gold_jejaring_vendor.csv")
    return JSONResponse(content=data)

# Mount the static dashboard files to the root ("/")
app.mount("/", StaticFiles(directory=str(DASHBOARD_DIR), html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
