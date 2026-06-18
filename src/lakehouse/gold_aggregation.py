import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
silver_file = BASE / "data/silver/silver_apbd_belanja.csv"

print(f"Membaca data dari Silver Layer: {silver_file}")
silver = pd.read_csv(silver_file)

# Melakukan agregasi untuk Ringkasan Anggaran per SKPD
gold_skpd = silver.groupby("nama_skpd").agg(
    total_pagu=("pagu_anggaran", "sum"),
    total_realisasi=("realisasi", "sum"),
    jumlah_proyek=("id", "count")
).reset_index()

out_dir = BASE / "data/gold"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "gold_skpd_summary.csv"

gold_skpd.to_csv(out_file, index=False, encoding="utf-8-sig")
print(f"Gold layer berhasil dibuat di: {out_file}")
print(gold_skpd.head())
