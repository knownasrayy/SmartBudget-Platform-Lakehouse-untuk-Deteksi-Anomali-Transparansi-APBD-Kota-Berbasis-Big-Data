import os
import glob
import pandas as pd
from pathlib import Path

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return max(files, key=os.path.getctime)

BASE = Path(__file__).resolve().parents[2]

bronze_pattern = str(BASE / "data/bronze/apbd_surabaya_raw_*.csv")
latest_bronze_file = get_latest_file(bronze_pattern)
print(f"Membaca file Bronze terbaru: {latest_bronze_file}")

sipd = pd.read_csv(latest_bronze_file)

silver = sipd.drop_duplicates().dropna(subset=["id", "anggaran", "realisasi"]).copy()

silver["anggaran"] = silver["anggaran"].astype("int64")
silver["realisasi"] = silver["realisasi"].astype("int64")

silver.rename(columns={"skpd": "nama_skpd", "anggaran": "pagu_anggaran"}, inplace=True)

if "kode_skpd" not in silver.columns: silver["kode_skpd"] = silver["nama_skpd"]
if "kode_rekening" not in silver.columns: silver["kode_rekening"] = silver["kategori_belanja"]
if "tanggal_kontrak" not in silver.columns: silver["tanggal_kontrak"] = silver["tanggal_input"]
if "id_vendor" not in silver.columns: silver["id_vendor"] = silver["id"]
if "id_transaksi" not in silver.columns: silver["id_transaksi"] = silver["id"]

out_dir = BASE / "data/silver"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "silver_apbd_belanja.csv"

silver.to_csv(out_file, index=False, encoding="utf-8-sig")
print(f"Silver layer berhasil dibuat di: {out_file}")
print(silver.head())
