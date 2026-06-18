import pandas as pd
import numpy as np
import uuid
from pathlib import Path
import calendar

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BRONZE_PATH = BASE_DIR / "data" / "bronze" / "ckan_apbd_raw.csv"
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver_apbd_belanja.csv"

def coalesce_columns(df, target_col, source_cols):
    """Gabungkan beberapa kolom menjadi satu kolom target dengan prioritas urutan."""
    df[target_col] = np.nan
    for col in source_cols:
        if col in df.columns:
            df[target_col] = df[target_col].fillna(df[col])
    return df

def process_ckan_to_silver():
    print("==============================================")
    print("=  PROCESSING CKAN DATA TO SILVER LAYER      =")
    print("==============================================")
    
    if not BRONZE_PATH.exists():
        print(f"Error: Raw file not found at {BRONZE_PATH}")
        return None
        
    df = pd.read_csv(BRONZE_PATH)
    print(f"Loaded {len(df)} rows from Bronze.")
    
    # Coalesce variation columns due to schema changes in CKAN over the years
    df = coalesce_columns(df, 'sektor_pajak', [
        'jenis_pendapatan_daerah_per_sektor', 'jenis_pendapatan_daerah_per_sek'
    ])
    
    df = coalesce_columns(df, 'target_anggaran', [
        'target_pendapatan_berdasarkan_apbd', 'target_pendapatan_berdasarkan_a', 'target_pendapatan'
    ])
    
    df = coalesce_columns(df, 'realisasi_uang', [
        'realisasi_pendapatan_daerah', 'realisasi_apbd', 'realisasi_penerimaan_pajak_daerah'
    ])
    
    # Fill missing SKPD
    if 'pd_penghasil' not in df.columns:
        df['pd_penghasil'] = "Badan Pendapatan Daerah"
    df['pd_penghasil'] = df['pd_penghasil'].fillna("Badan Pendapatan Daerah")
    
    # Drop rows without revenue target or realization
    df = df.dropna(subset=['target_anggaran', 'realisasi_uang'], how='all').copy()
    
    # Fill NaN with 0 for numerics
    df['target_anggaran'] = pd.to_numeric(df['target_anggaran'], errors='coerce').fillna(0)
    df['realisasi_uang'] = pd.to_numeric(df['realisasi_uang'], errors='coerce').fillna(0)
    
    # Ensure strings
    df['sektor_pajak'] = df['sektor_pajak'].astype(str).str.strip()
    df['sektor_pajak'] = df['sektor_pajak'].replace('nan', 'Pendapatan Lain-lain')
    
    # MAPPING TO MEDALLION 'BELANJA' SCHEMA (for Anomaly Engine compatibility)
    df_silver = pd.DataFrame()
    
    # Generate UUIDs
    df_silver['id_transaksi'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Date mapping
    years = pd.to_numeric(df['_extracted_year'], errors='coerce').fillna(2023).astype(int)
    months = pd.to_numeric(df['_extracted_month'], errors='coerce').fillna(1).astype(int)
    # Clip months to 1-12
    months = months.clip(1, 12)
    # Generate end of month date string
    def get_date(y, m):
        d = calendar.monthrange(y, m)[1]
        return f"{y}-{m:02d}-{d:02d}"
        
    df_silver['tanggal_kontrak'] = [get_date(y, m) for y, m in zip(years, months)]
    df_silver['tahun_anggaran'] = years
    df_silver['bulan_kontrak'] = months
    
    df_silver['kota'] = 'Surabaya'
    df_silver['kode_skpd'] = 'SKPD-BAPENDA'
    df_silver['nama_skpd'] = df['pd_penghasil']
    df_silver['kode_rekening'] = '4.1.' + (df.index.astype(str)) # Fake rekening code for revenue
    df_silver['uraian_belanja'] = df['sektor_pajak'] # mapped to belanja to keep model running
    
    df_silver['pagu_anggaran'] = df['target_anggaran'].fillna(0)
    df_silver['realisasi'] = df['realisasi_uang'].fillna(0)
    
    # Safe percentage calculation
    df_silver['persen_realisasi'] = np.where(
        df_silver['pagu_anggaran'] > 0,
        (df_silver['realisasi'] / df_silver['pagu_anggaran']) * 100,
        0.0
    )
    
    # Map vendor for graph functionality
    df_silver['nama_vendor'] = "Wajib Pajak (Agregat)"
    df_silver['id_vendor'] = "WP-001"
    df_silver['jenis_pengadaan'] = "Penerimaan Pajak"
    
    print(f"Mapped {len(df_silver)} rows to Silver Schema.")
    print("Sample:\n", df_silver[['uraian_belanja', 'pagu_anggaran', 'realisasi']].head())
    
    # Save to Silver
    SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_silver.to_csv(SILVER_PATH, index=False)
    print(f"✅ Successfully saved mapped data to {SILVER_PATH}")
    
    return df_silver

if __name__ == "__main__":
    process_ckan_to_silver()
