# 🏛️ SmartBudget Lakehouse: Platform Deteksi Anomali & Transparansi APBD Berbasis Big Data

![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Medallion_Lakehouse-orange)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-Isolation_Forest-yellow)

**SmartBudget Lakehouse** adalah platform *Big Data* komprehensif yang dirancang untuk memantau, mendeteksi anomali, dan meningkatkan transparansi pada Anggaran Pendapatan dan Belanja Daerah (APBD) Kota Surabaya. Platform ini menggabungkan arsitektur *Medallion Data Lakehouse*, *Machine Learning* untuk deteksi penipuan (*fraud*), dan *Natural Language Processing* (NLP) untuk analisis sentimen publik.

---

## ✨ Fitur Utama

*   **🔍 Deteksi Anomali Anggaran (ML Engine)**: Menggunakan algoritma *Isolation Forest* dan *Z-Score* untuk mengidentifikasi transaksi atau pengadaan barang/jasa yang mencurigakan secara otomatis.
*   **📊 Arsitektur Medallion Lakehouse**: Pengelolaan data multi-zona (*Bronze* untuk data mentah, *Silver* untuk data bersih, *Gold* untuk agregasi analitik) yang menjamin integritas dan performa *query* data.
*   **🌐 Real-Time Data Ingestion**: Menarik data dunia nyata dari berbagai sumber melalui *API* dan *Scraping*:
    *   Data Portal Terbuka Pemerintah (CKAN APBD Surabaya & LPSE).
    *   Data Sentimen Publik (Komentar YouTube, Google News, RSS, Twitter/X).
*   **🗺️ Pemetaan Spasial Anomali**: *Dashboard* interaktif yang terintegrasi dengan Leaflet.js untuk memvisualisasikan peta risiko (Waspada, Kritis, Aman) per kecamatan di Surabaya (*Heatmap*).
*   **🗣️ Analisis Sentimen Publik (NLP)**: Mengevaluasi opini masyarakat terhadap kebijakan dan proyek infrastruktur pemerintah secara proaktif menggunakan algoritma heuristik & *Machine Learning*.
*   **🕸️ Analisis Jejaring Entitas**: Melacak hubungan dan jejaring vendor penyedia layanan untuk mendeteksi monopoli atau indikasi *fraud* dalam tender pemerintah.

---

## 🏗️ Arsitektur Sistem

Sistem ini dibangun dengan mengadopsi pola **Medallion Architecture**:
1.  **Bronze Layer**: Menyimpan data mentah murni hasil ekstraksi (*ingestion*) dari API (JSON, CSV, dll.) tanpa modifikasi.
2.  **Silver Layer**: Memproses, membersihkan (*cleansing*), memformat, dan melakukan *join* data dari berbagai sumber (menggunakan *Pandas/PySpark*).
3.  **Gold Layer**: Data analitik yang sudah teragregasi dan di-*scoring* oleh model *Machine Learning* (seperti `apbd_scored.csv` dan `gold_skpd_summary.csv`), siap disajikan ke *Dashboard*.

---

## 🛠️ Tech Stack

*   **Data Ingestion & Scraping**: Python, `requests`, `BeautifulSoup`, `google-api-python-client`, `apify-client`, `feedparser`.
*   **Data Engineering & Lakehouse**: Python, `pandas`, PySpark (direncanakan).
*   **Machine Learning & NLP**: `scikit-learn` (Isolation Forest), `numpy`, NLP Text Processing.
*   **Frontend Dashboard**: HTML5, Vanilla JavaScript, Tailwind CSS (Visual/UI), Leaflet.js (Pemetaan Spasial), PapaParse (CSV Parsing).
*   **Backend Server**: Python HTTP Server / Streamlit.

---

## 📂 Struktur Direktori

```text
├── data/
│   ├── bronze/          # Data mentah hasil ekstraksi API & Scraper
│   ├── silver/          # Data yang telah dibersihkan dan diformat
│   └── gold/            # Data agregat akhir dan hasil prediksi ML
├── src/
│   ├── dashboard/       # Frontend HTML, CSS, JS, dan Streamlit App
│   ├── ingestion/       # Script penarik data (GNews, YouTube, CKAN, LPSE, dll)
│   ├── lakehouse/       # Transformasi data Silver ke Gold
│   ├── ml_engine/       # Algoritma Machine Learning (Deteksi Anomali)
│   └── nlp_engine/      # Pemrosesan Natural Language dan Sentimen
├── requirements.txt     # Daftar dependensi Python
├── run_server.py        # Script untuk menjalankan web server lokal
├── run_ingestion.sh     # Script eksekusi pipeline data massal
└── README.md            # Dokumentasi ini
```

---

## 🚀 Cara Instalasi dan Penggunaan

### 1. Prasyarat
*   Python 3.9 atau lebih baru.
*   *Git* terinstal.

### 2. Kloning Repositori
```bash
git clone https://github.com/knownasrayy/SmartBudget-Platform-Lakehouse-untuk-Deteksi-Anomali-Transparansi-APBD-Kota-Berbasis-Big-Data.git
cd SmartBudget-Platform-Lakehouse-untuk-Deteksi-Anomali-Transparansi-APBD-Kota-Berbasis-Big-Data
```

### 3. Konfigurasi Lingkungan Virtual
Sangat disarankan menggunakan *virtual environment* Python:
```bash
python -m venv .venv

# Untuk Windows:
.venv\Scripts\activate

# Untuk Linux/Mac:
source .venv/bin/activate
```

### 4. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 5. Konfigurasi API Keys (Environment Variables)
Buat file `.env` di direktori *root* dan masukkan API Keys Anda (jika Anda ingin menjalankan *ingestion* data publik yang sebenarnya):
```env
YOUTUBE_API_KEY=your_api_key_here
GNEWS_API_KEY=your_api_key_here
```

### 6. Menjalankan Pipeline Data (Opsional)
Jika Anda ingin memperbarui data *Lakehouse* secara manual:
```bash
# Menjalankan transformasi data mentah ke zona Gold
python src/ml_engine/pipeline.py
```

### 7. Menjalankan Dashboard Interaktif
Untuk melihat hasil visualisasi di *browser*:
```bash
# Menjalankan server web statis
python -m http.server 8000
```
Buka `http://localhost:8000/src/dashboard/index.html` di *browser* Anda.

*(Alternatif: Tersedia juga versi purwarupa Streamlit yang dapat dijalankan dengan `streamlit run src/dashboard/app.py`)*

---

## 🔮 Rencana Pengembangan Selanjutnya (Roadmap)
*   [ ] Integrasi **Apache Spark (PySpark)** untuk penanganan data dalam skala *Big Data* yang sesungguhnya.
*   [ ] Mengganti algoritma NLP heuristik *browser* dengan **HuggingFace Transformers (IndoBERT)** untuk klasifikasi sentimen yang sangat akurat.
*   [ ] Mengubah arsitektur *backend* statis menjadi sistem API dinamis menggunakan **FastAPI** atau **Flask**.
*   [ ] Otomatisasi jalur pipa data (*pipeline orchestration*) menggunakan **Apache Airflow**.

---

## 👥 Kontributor
Dibuat dengan ❤️ sebagai bentuk inovasi transparansi pemerintahan berbasis Big Data.
