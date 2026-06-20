# 🏛️ SmartBudget Lakehouse: Platform Deteksi Anomali & Transparansi APBD Berbasis Big Data

![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Big Data](https://img.shields.io/badge/Big_Data-Apache_Spark-orange)
![Orchestration](https://img.shields.io/badge/Orchestration-Apache_Airflow-red)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)

**SmartBudget Lakehouse** adalah platform *Big Data* berskala *Enterprise* yang dirancang untuk memantau, mendeteksi anomali (indikasi *fraud* atau *markup*), dan mensinkronkan transparansi Anggaran Pendapatan dan Belanja Daerah (APBD) Kota Surabaya dengan sentimen publik. 

Proyek ini mendemonstrasikan implementasi **Medallion Data Lakehouse Architecture** murni menggunakan ekosistem *Big Data* sesungguhnya (*Apache Spark*, *Delta Lake*, *Apache Airflow*) yang dikombinasikan dengan *Machine Learning* dan *Natural Language Processing* (NLP).

---

## ✨ Fitur Utama & Inovasi Solusi

*   **📊 Arsitektur Medallion Lakehouse (PySpark & Delta Lake)**: Pengelolaan data multi-zona (*Bronze*, *Silver*, *Gold*) menggunakan *engine* terdistribusi **PySpark**. Data disimpan dalam format **Delta Lake** untuk menjamin integritas data (ACID *transactions*) dan performa *query* tingkat tinggi.
*   **🔍 Deteksi Anomali Anggaran (Spark MLlib)**: Menggunakan algoritma **K-Means Clustering** dari *Spark MLlib* untuk mencari deviasi jarak (Euclidean) dan *Z-Score*, mengidentifikasi pengadaan barang/jasa yang secara statistik sangat mencurigakan secara otomatis.
*   **⚙️ Otomatisasi Pipeline (Apache Airflow)**: Seluruh alur data (*Ingestion -> Silver Transform -> MLlib Scoring -> Gold Publish*) diorkestrasi secara otomatis (DAGs) dan terjadwal menggunakan **Apache Airflow**.
*   **🌐 Multi-Source Data Ingestion**: Menarik data dunia nyata yang berukuran masif secara *real-time*:
    *   **Data Terstruktur**: Portal Open Data Pemkot Surabaya (CKAN API).
    *   **Data Tak Terstruktur (Teks)**: *Scraping* opini publik dan aduan warga menggunakan **Apify** (Twitter/X), **YouTube API** (Komentar), dan **Google News**.
*   **🗣️ Analisis Sentimen Publik (NLP)**: Mengklasifikasikan opini masyarakat secara proaktif untuk membandingkan tingkat kepuasan warga dengan jumlah realisasi anggaran di suatu dinas.
*   **🗺️ Visualisasi & Forensik Interaktif**: UI/UX memukau dibangun di atas **FastAPI** (Backend) dan Vanilla JavaScript + Tailwind CSS + Leaflet.js (Frontend) untuk pemetaan spasial anomali (*Heatmap*) dan pelacakan jejaring entitas/vendor.

---

## 🏗️ Desain Infrastruktur & Arsitektur Sistem

Sistem ini mematuhi standar arsitektur **Medallion**:

1.  **🥉 Bronze Layer (Ingestion)**:
    *   **Tujuan**: Menyimpan data mentah murni hasil ekstraksi dari API (JSON/CSV) tanpa modifikasi.
    *   **Teknologi**: Python `requests`, `apify-client`, `google-api-python-client`.
2.  **🥈 Silver Layer (Cleansing & Conforming)**:
    *   **Tujuan**: Pembersihan tipe data, penanganan *Null*, dedah (*parsing*) tanggal, dan standardisasi skema.
    *   **Teknologi**: **PySpark DataFrame API** menyimpan output dalam format direktori **Delta Lake**.
3.  **🥇 Gold Layer (Analytics & ML)**:
    *   **Tujuan**: Tabel agregasi akhir untuk dasbor (seperti ringkasan SKPD) dan penilaian Anomali (*Scored Data*).
    *   **Teknologi**: **Spark MLlib** (VectorAssembler, StandardScaler, KMeans) mengekspor data ke dalam Delta Lake & CSV yang siap di-*serve*.
4.  **🚀 Serving Layer**:
    *   **Teknologi**: **FastAPI** (`src/api/main.py`) membaca *Gold Layer* dan mengeksposnya sebagai *endpoint* REST API berkecepatan tinggi (`/api/anomalies`, `/api/summary`) untuk dikonsumsi oleh *Frontend Dashboard*.

---

## 📂 Struktur Direktori

```text
├── dags/                # Apache Airflow DAGs (smartbudget_pipeline.py)
├── data/
│   ├── bronze/          # Data mentah ekstraksi API & Scraper
│   ├── silver/          # Delta Lake format (Data Bersih)
│   └── gold/            # Delta Lake & CSV (Data Agregat & Prediksi ML)
├── src/
│   ├── api/             # FastAPI Backend Server (main.py)
│   ├── dashboard/       # Frontend UI (HTML, Tailwind CSS, JS, Leaflet)
│   ├── ingestion/       # Script penarik data (CKAN, Apify, GNews, YouTube)
│   ├── lakehouse/       # Transformasi Silver & Gold (PySpark)
│   └── ml_engine/       # Algoritma Spark MLlib K-Means (anomaly_detector.py)
├── requirements.txt     # Dependensi Python
├── run_pyspark.ps1      # Wrapper eksekusi PySpark untuk environment Windows
├── run_server.py        # Script untuk menjalankan FastAPI (Port 8080)
└── README.md            # Dokumentasi
```

---

## 🚀 Cara Instalasi dan Penggunaan

### 1. Prasyarat Sistem
*   **Python 3.9+** terinstal.
*   **Java (JDK 8/11)** terinstal dan *Environment Variable* `JAVA_HOME` telah dikonfigurasi (wajib untuk Apache Spark).
*   *Hadoop winutils* (jika menggunakan Windows, agar PySpark dapat menulis *filesystem* dengan lancar).

### 2. Kloning Repositori & Virtual Environment
```bash
git clone https://github.com/knownasrayy/Big-Data-Data-Lakehouse.git
cd Big-Data-Data-Lakehouse

# Konfigurasi Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # (Windows)
# atau: source .venv/bin/activate (Linux/Mac)
```

### 3. Instalasi Dependensi Terkait
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Kredensial (Opsional untuk Ingestion)
Buat file `.env` di direktori *root* untuk menjalankan proses tarik data aktual dari internet:
```env
YOUTUBE_API_KEY=your_api_key_here
GNEWS_API_KEY=your_api_key_here
APIFY_TOKEN=your_apify_token_here
```

### 5. Menjalankan Pipa Data (PySpark Lakehouse)
Jika Anda menggunakan OS Windows, eksekusi menggunakan *wrapper* PowerShell yang sudah disediakan untuk menghindari *error gateway* Java:
```powershell
# 1. Tarik data (Simulasi/API)
python src/ingestion/ingest_ckan_apbd.py
python src/ingestion/ingest_apify_twitter.py

# 2. Proses Medallion (Silver -> Gold -> MLlib)
.\run_pyspark.ps1 src\lakehouse\silver_transform.py
.\run_pyspark.ps1 src\ml_engine\anomaly_detector.py
```
*(Catatan: Anda juga bisa mengotomatisasi ini jika menjalankan **Apache Airflow**).*

### 6. Menjalankan Dashboard (FastAPI Backend)
Jalankan server aplikasi utama untuk mengakses *Dashboard* Interaktif:
```bash
python run_server.py
```
Akses *dashboard* di *browser* pada tautan: **http://localhost:8080**

---

## 🏆 Standar Kompetisi & Penilaian (Gemastik)
Proyek ini dikembangkan dengan kerangka standar industri yang sangat relevan untuk dikompetisikan dalam ajang nasional seperti **GEMASTIK** pada kategori *Kota Cerdas (Smart City)* atau *Penambangan Data (Data Mining)*:
*   Mendemonstrasikan penerapan nyata **Big Data** dan mengatasi *silo data* (gabungan data struktur pemda & teks media sosial).
*   Menerapkan arsitektur skalabel (*Separation of Compute and Storage*).
*   Berfokus pada penyelesaian masalah sosial-ekonomi ber-dampak tinggi (pemberantasan korupsi dan optimalisasi anggaran).

---
*Dibuat untuk merevolusi transparansi pemerintahan berbasis Big Data dan Kecerdasan Buatan.*
