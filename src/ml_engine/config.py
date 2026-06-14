"""
config.py — Konfigurasi global untuk SmartBudget ML Engine.
Semua path, hyperparameter, dan konstanta didefinisikan di sini.
"""

import os
from pathlib import Path

# ============================================================
# PATH CONFIGURATION
# ============================================================

# Root project
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data directories (Medallion Architecture)
DATA_DIR = PROJECT_ROOT / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

# ML Engine output
ML_OUTPUT_DIR = DATA_DIR / "ml_output"
PLOTS_DIR = ML_OUTPUT_DIR / "plots"

# Pastikan semua direktori ada
for d in [BRONZE_DIR, SILVER_DIR, GOLD_DIR, ML_OUTPUT_DIR, PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# DATA GENERATION CONFIG
# ============================================================

# Kota-kota yang di-cover (Jawa Timur)
KOTA_LIST = [
    "Kota Surabaya",
    "Kota Malang",
    "Kabupaten Sidoarjo",
    "Kabupaten Gresik",
    "Kota Mojokerto",
]

# SKPD (Satuan Kerja Perangkat Daerah) — sample realistis
SKPD_LIST = [
    {"kode": "1.01", "nama": "Dinas Pendidikan"},
    {"kode": "1.02", "nama": "Dinas Kesehatan"},
    {"kode": "1.03", "nama": "Dinas Pekerjaan Umum dan Penataan Ruang"},
    {"kode": "1.04", "nama": "Dinas Perumahan dan Kawasan Permukiman"},
    {"kode": "1.05", "nama": "Satuan Polisi Pamong Praja"},
    {"kode": "1.06", "nama": "Dinas Sosial"},
    {"kode": "2.01", "nama": "Dinas Tenaga Kerja"},
    {"kode": "2.02", "nama": "Dinas Lingkungan Hidup"},
    {"kode": "2.03", "nama": "Dinas Kependudukan dan Pencatatan Sipil"},
    {"kode": "2.04", "nama": "Dinas Perhubungan"},
    {"kode": "2.05", "nama": "Dinas Komunikasi dan Informatika"},
    {"kode": "3.01", "nama": "Dinas Penanaman Modal dan PTSP"},
    {"kode": "3.02", "nama": "Dinas Kepemudaan dan Olahraga"},
    {"kode": "3.03", "nama": "Dinas Kebudayaan dan Pariwisata"},
    {"kode": "4.01", "nama": "Badan Perencanaan Pembangunan Daerah"},
    {"kode": "4.02", "nama": "Badan Pengelolaan Keuangan dan Aset Daerah"},
    {"kode": "4.03", "nama": "Badan Kepegawaian Daerah"},
    {"kode": "5.01", "nama": "Sekretariat Daerah"},
    {"kode": "5.02", "nama": "Sekretariat DPRD"},
    {"kode": "5.03", "nama": "Inspektorat"},
]

# Kode rekening belanja (mengikuti format SIPD)
KODE_REKENING_BELANJA = {
    "5.1.01": "Belanja Pegawai - Gaji dan Tunjangan",
    "5.1.02": "Belanja Pegawai - Tambahan Penghasilan",
    "5.1.03": "Belanja Pegawai - Honorarium",
    "5.2.01": "Belanja Barang - ATK dan Perlengkapan",
    "5.2.02": "Belanja Barang - Jasa Konsultansi",
    "5.2.03": "Belanja Barang - Jasa Lainnya",
    "5.2.04": "Belanja Barang - Pemeliharaan",
    "5.2.05": "Belanja Barang - Perjalanan Dinas",
    "5.2.06": "Belanja Barang - Cetak dan Penggandaan",
    "5.2.07": "Belanja Barang - Makan Minum",
    "5.2.08": "Belanja Barang - Sewa",
    "5.3.01": "Belanja Modal - Tanah",
    "5.3.02": "Belanja Modal - Peralatan dan Mesin",
    "5.3.03": "Belanja Modal - Gedung dan Bangunan",
    "5.3.04": "Belanja Modal - Jalan, Irigasi, dan Jaringan",
    "5.3.05": "Belanja Modal - Aset Tetap Lainnya",
    "5.4.01": "Belanja Hibah",
    "5.4.02": "Belanja Bantuan Sosial",
}

# Jenis pengadaan
JENIS_PENGADAAN = [
    "Pengadaan Langsung",
    "Tender",
    "E-Purchasing",
    "Seleksi",
    "Penunjukan Langsung",
]

# ============================================================
# SYNTHETIC DATA CONFIG
# ============================================================

SYNTHETIC_NUM_TRANSACTIONS = 5000
SYNTHETIC_NUM_VENDORS = 200
SYNTHETIC_ANOMALY_RATE = 0.05        # 5% anomali transaksi
SYNTHETIC_FRAUD_VENDOR_RATE = 0.10   # 10% vendor fraud
SYNTHETIC_YEARS = [2022, 2023, 2024, 2025]
RANDOM_SEED = 42

# ============================================================
# ANOMALY DETECTION CONFIG
# ============================================================

# Benford's Law
BENFORD_SIGNIFICANCE_LEVEL = 0.05    # Alpha untuk chi-square test
BENFORD_MIN_SAMPLES = 50            # Minimum sample per grup

# Isolation Forest
IF_N_ESTIMATORS = 200
IF_CONTAMINATION = 0.05
IF_RANDOM_STATE = 42

# Z-Score
ZSCORE_THRESHOLD = 3.0
IQR_MULTIPLIER = 1.5

# Ensemble
ENSEMBLE_WEIGHTS = {
    "benford": 0.25,
    "isolation_forest": 0.45,
    "zscore": 0.30,
}
RISK_THRESHOLDS = {
    "low": 25,
    "medium": 50,
    "high": 75,
    # >= 75 = critical
}

# ============================================================
# GRAPH ANALYSIS CONFIG
# ============================================================

# Entity Resolution
FUZZY_MATCH_THRESHOLD = 85           # Minimum similarity score (0-100)

# Community Detection
LOUVAIN_RESOLUTION = 1.0

# Risk Scoring (graph-based)
GRAPH_RISK_WEIGHTS = {
    "shared_address": 30,
    "shared_director": 30,
    "new_vendor_big_contract": 20,
    "dominant_in_skpd": 25,
    "high_pagerank_low_contracts": 25,
}

# ============================================================
# VISUALIZATION CONFIG
# ============================================================

PLOT_STYLE = "seaborn-v0_8-darkgrid"
PLOT_DPI = 150
PLOT_FIGSIZE = (12, 7)
COLOR_PALETTE = {
    "normal": "#2ecc71",
    "anomaly": "#e74c3c",
    "warning": "#f39c12",
    "primary": "#3498db",
    "secondary": "#9b59b6",
}
