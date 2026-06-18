# 🏛️ SmartAPBD

**Lakehouse-Based Anomaly Detection Platform for Regional Budget Transparency in Indonesian Smart Cities**

> *Karena Smart City yang sesungguhnya bukan tentang teknologinya — tapi tentang siapa yang diuntungkan dari setiap rupiah anggaran publik.*

---

## 📌 Overview

SmartAPBD adalah platform Big Data Lakehouse yang dirancang untuk mendeteksi anomali dan meningkatkan transparansi anggaran daerah (APBD) di Indonesia secara otomatis dan near real-time.

Platform ini mengintegrasikan data publik dari portal SIPD Kemendagri, laporan audit BPK, berita media, dan sentimen warga ke dalam satu pipeline streaming berbasis **Apache Kafka** dan **Delta Lake** dengan arsitektur **Medallion (Bronze–Silver–Gold)**. Melalui pendekatan **Machine Learning (Isolation Forest)** dan **NLP**, sistem mampu menandai pos belanja janggal, pola mark-up anggaran, dan ketidaksesuaian realisasi secara proaktif.

| Kriteria | Pemenuhan |
|---|---|
| ✅ **Riil** | Dugaan korupsi APBD Surabaya 2025, 70+ OTT KPK 2023–2025 |
| ✅ **Unik** | Belum ada sistem lakehouse open-source untuk deteksi anomali APBD Indonesia |
| ✅ **Berdampak** | Data SIPD + BPK + NLP berita → early warning penyimpangan anggaran |
| ✅ **Inovatif** | Kafka + Delta Lake + Spark + Isolation Forest + NLP + Dashboard real-time |

---

## 🔴 Latar Belakang & Masalah

Korupsi anggaran daerah adalah masalah sistemik yang terus berulang:

- **70+ kepala daerah** ditangkap KPK dalam OTT sepanjang 2023–2025
- **September 2025**: Demo mahasiswa di Balai Kota Surabaya terkait dugaan korupsi APBD Surabaya 2025 — anggaran perjalanan dinas hingga Rp 11,7 juta/hari (standar Kemenkeu: Rp 9,5 juta/hari)
- Tren korupsi semakin canggih: perusahaan fiktif, manipulasi data elektronik, pemalsuan dokumen
- Mekanisme pengawasan masih **manual, reaktif, dan tidak berbasis data real-time**

**Gap yang belum terisi**: Belum ada sistem lakehouse terbuka yang secara otomatis mengkrawl, mengintegrasikan, dan mendeteksi anomali dari data APBD publik lintas kota.

### Analisis Kompetitor

| Solusi Existing | Kelebihan | Keterbatasan |
|---|---|---|
| Portal SIPD Kemendagri | Data APBD terpusat | Tidak ada fitur deteksi anomali, hanya storage |
| e-Budgeting Pemda | Input anggaran terdigitalisasi | Tidak lintas kota, tidak ada analitik lanjutan |
| Laporan Audit BPK | Kredibel dan resmi | Tahunan, manual, tidak real-time |
| Indonesia Corruption Watch | Watchdog aktif | Berbasis investigasi manual, tidak scalable |

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                          │
│  SIPD Kemendagri  │  BPK (PDF)  │  NewsAPI/RSS  │  Twitter  │
└────────┬──────────┴──────┬──────┴──────┬─────────┴────┬─────┘
         │                 │             │               │
         └─────────────────┴─────────────┴───────────────┘
                                    │
                            ┌───────▼────────┐
                            │  Apache Kafka  │  (Streaming / Batch Ingestion)
                            └───────┬────────┘
                                    │
              ┌─────────────────────▼──────────────────────┐
              │              DELTA LAKE                    │
              │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
              │  │  Bronze  │→ │  Silver  │→ │   Gold   │ │
              │  │  Raw     │  │ Cleaned  │  │Analytics │ │
              │  └──────────┘  └──────────┘  └──────────┘ │
              └─────────────────────┬──────────────────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
             ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
             │  Isolation   │ │   NLP    │ │   Graph    │
             │   Forest     │ │Sentiment │ │  Analysis  │
             │  (Anomaly)   │ │(IndoBERT)│ │  (Aliran   │
             └───────┬──────┘ └────┬─────┘ │   Dana)    │
                     │              │       └─────┬──────┘
                     └──────────────┴─────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │   Streamlit Dashboard  │
                        │  Heatmap Anomali │ KPI │
                        └───────────────────────┘
```

### Layer Medallion Architecture

| Layer | Deskripsi | Contoh Data |
|---|---|---|
| **Bronze** | Raw ingestion — data mentah tanpa transformasi | JSON SIPD, PDF BPK, tweet raw |
| **Silver** | Cleaned & enriched — normalisasi, ekstraksi entitas | Anggaran per pos, entitas nama pejabat |
| **Gold** | Analytics-ready — agregasi, anomaly score, time-series | Anomali per kota, trend realisasi vs. anggaran |

---

## 🛠️ Tech Stack

| Kategori | Teknologi |
|---|---|
| **Ingestion** | Apache Kafka, Python Scrapy / BeautifulSoup |
| **Storage** | Delta Lake (MinIO / HDFS lokal) |
| **Processing** | Apache Spark (PySpark) |
| **Anomaly Detection** | Scikit-learn — Isolation Forest, Z-score |
| **NLP** | IndoBERT (HuggingFace Transformers) |
| **Orchestration** | Apache Airflow (opsional) / Cron job |
| **Dashboard** | Streamlit |
| **Containerization** | Docker, Docker Compose |

---

## 📦 Sumber Data

### 🟢 Data Primer (Prioritas)
| Sumber | Metode | Konten |
|---|---|---|
| SIPD Kemendagri (`sipd.kemendagri.go.id`) | Web Scraping | Realisasi APBD per kota/kabupaten |
| Twitter/X API v2 | Streaming API | Tweet keyword: korupsi APBD, mark-up anggaran |
| NewsAPI / RSS Media | REST API | Berita Detik, Kompas, Republika terkait anggaran |

### 🟡 Data Sekunder
| Sumber | Metode | Konten |
|---|---|---|
| BPK (`bpk.go.id`) | PDF Scraping | Laporan Hasil Pemeriksaan per daerah |
| Open Data Surabaya (`data.surabaya.go.id`) | API / CSV Download | Historis APBD Surabaya |
| `data.go.id` | API | Data APBD lintas kabupaten/kota |

### 🔵 Scope Demo (Week 16)
- **Kota fokus**: Surabaya (utama) + Malang (pembanding)
- **Periode**: APBD 2024–2025
- **Kategori belanja**: Perjalanan Dinas, Pengadaan Barang/Jasa, Belanja Hibah

---

## 🤖 Machine Learning Pipeline

### 1. Anomaly Detection — Isolation Forest
```python
from sklearn.ensemble import IsolationForest

features = [
    'realisasi_persen',       # % realisasi vs. anggaran
    'nominal_anggaran',       # Total anggaran pos
    'delta_dari_median',      # Deviasi dari median kategori
    'rasio_perjalanan_dinas', # Proporsi perdin dari total belanja
]

model = IsolationForest(contamination=0.05, random_state=42)
df['anomaly_score'] = model.fit_predict(df[features])
df['is_anomaly'] = df['anomaly_score'] == -1
```

### 2. NLP Sentiment — Sinyal Berita
```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="indobenchmark/indobert-base-p2"
)

# Analisis sentimen berita terkait anggaran kota target
df['sentiment'] = df['headline'].apply(lambda x: classifier(x)[0]['label'])
```

### 3. Z-Score per Kategori Belanja
```python
from scipy import stats

# Deteksi outlier dalam kategori yang sama
df['z_score'] = df.groupby('kategori_belanja')['nominal'].transform(
    lambda x: stats.zscore(x, nan_policy='omit')
)
df['is_outlier'] = df['z_score'].abs() > 2.5
```

---

## 📁 Struktur Direktori

```
smartapbd/
├── docker-compose.yml          # Kafka + MinIO + Spark + Airflow
├── requirements.txt
├── README.md
│
├── ingestion/
│   ├── scrapers/
│   │   ├── sipd_scraper.py     # SIPD Kemendagri scraper
│   │   ├── bpk_pdf_parser.py   # PDF BPK extractor
│   │   └── news_rss.py         # NewsAPI / RSS fetcher
│   └── kafka_producer.py       # Kirim data ke Kafka topic
│
├── lakehouse/
│   ├── bronze/
│   │   └── ingest_raw.py       # Kafka consumer → Delta Bronze
│   ├── silver/
│   │   └── transform.py        # Cleaning, normalisasi, ekstraksi entitas
│   └── gold/
│       └── aggregate.py        # Agregasi anomali, feature engineering
│
├── ml/
│   ├── anomaly_detection.py    # Isolation Forest + Z-score
│   ├── nlp_sentiment.py        # IndoBERT sentiment pipeline
│   └── train.py                # Training & evaluasi model
│
├── dashboard/
│   ├── app.py                  # Streamlit main app
│   ├── components/
│   │   ├── heatmap.py          # Heatmap anomali per kota
│   │   ├── timeseries.py       # Trend realisasi vs. anggaran
│   │   └── anomaly_table.py    # Tabel detail pos janggal
│   └── assets/
│
└── notebooks/
    ├── 01_exploration.ipynb    # EDA data APBD
    ├── 02_modeling.ipynb       # Eksperimen model anomali
    └── 03_nlp_pipeline.ipynb  # NLP sentiment tuning
```

---

## 🚀 Cara Menjalankan

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Java 11+ (untuk Spark)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/username/smartapbd.git
cd smartapbd

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Jalankan Infrastruktur
```bash
docker-compose up -d
# Menjalankan: Kafka, MinIO (Delta Lake), Spark, Airflow
```

### 3. Ingest Data
```bash
# Scraping SIPD Surabaya
python ingestion/scrapers/sipd_scraper.py --kota surabaya --tahun 2025

# PDF BPK
python ingestion/scrapers/bpk_pdf_parser.py --input data/bpk_2025/

# News sentiment
python ingestion/scrapers/news_rss.py --keywords "korupsi APBD,mark-up anggaran"
```

### 4. Jalankan Pipeline Lakehouse
```bash
# Bronze → Silver → Gold
python lakehouse/bronze/ingest_raw.py
python lakehouse/silver/transform.py
python lakehouse/gold/aggregate.py
```

### 5. Latih Model & Deteksi Anomali
```bash
python ml/anomaly_detection.py --kota surabaya --tahun 2025
```

### 6. Jalankan Dashboard
```bash
streamlit run dashboard/app.py
# Buka: http://localhost:8501
```

---

## 📊 Output & Demo

Dashboard Streamlit menampilkan:

1. **Heatmap Anomali** — visualisasi intensitas anomali per kota dan per kategori belanja
2. **Time-series Realisasi** — perbandingan anggaran vs. realisasi per kuartal
3. **Tabel Pos Janggal** — detail pos belanja dengan anomaly score tertinggi, dilengkapi link sumber
4. **Sentiment Monitor** — sinyal media dan Twitter terkait kota target

### Contoh Temuan (Demo Case: Surabaya 2025)
```
⚠️  ANOMALI TERDETEKSI

Pos    : Perjalanan Dinas Luar Negeri
Anggaran: Rp 8,600,000,000
Tarif  : Rp 11,700,000 / hari (standar: Rp 9,500,000)
Z-Score: 3.2 (OUTLIER)
Sumber : SIPD Surabaya 2025-Q3
```

---

## 🗓️ Timeline

| Week | Fase | Target |
|---|---|---|
| **Week 15** (sekarang) | Desain & Persiapan | Arsitektur final, setup environment, Bronze layer SIPD Surabaya |
| **Week 16** | Demo Final | End-to-end pipeline + anomaly detection + Streamlit dashboard |
| **Week 17** | Revisi | Polish UI, tambah NLP sentimen, dokumentasi akhir |

---

## 🌱 Potensi Pengembangan

- **Scale nasional**: 514 kabupaten/kota Indonesia dengan pipeline yang sama
- **Integrasi LKPP**: Deteksi anomali pengadaan barang/jasa pemerintah
- **Open-source Civic Tech**: Tool untuk ICW, TII, dan lembaga antikorupsi
- **Real-time streaming**: Migrasi dari batch ke full Kafka streaming
- **Graph analytics**: Deteksi pola aliran dana antar-entitas (jejaring korupsi)

---

## 👥 Tim

| Nama | Role |
|---|---|
| [Nama Anggota 1] | Data Engineering & Lakehouse Architecture |
| [Nama Anggota 2] | ML Pipeline & Anomaly Detection |
| [Nama Anggota 3] | Scraping, NLP, Dashboard |

---

## 📄 Lisensi

MIT License — Proyek ini bersifat open-source dan dapat digunakan untuk kepentingan riset dan civic technology.

---

> **SmartAPBD** | Final Project Big Data & Lakehouse | Institut Teknologi Sepuluh Nopember | 2026