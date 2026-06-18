# 🏛️ SmartBudget: Platform Lakehouse untuk Deteksi Anomali & Transparansi APBD Kota

[![Target](https://img.shields.io/badge/Target-Week%2016%20Demo-red?style=flat-square)](#)
[![Category](https://img.shields.io/badge/Category-Smart%20Governance%20%26%20Civic%20Tech-blue?style=flat-square)](#)
[![Tech Stack](https://img.shields.io/badge/Tech-Spark%20%7C%20Delta%20Lake%20%7C%20NLP-orange?style=flat-square)](#)

**SmartBudget** adalah platform *Big Data Lakehouse* terintegrasi yang dirancang untuk mendukung pilar *Smart Governance* dalam ekosistem *Smart City*. Platform ini secara otomatis mengumpulkan, memproses, dan mendeteksi anomali pada data Anggaran Pendapatan dan Belanja Daerah (APBD) menggunakan pendekatan komputasi terdistribusi, *Machine Learning*, dan pemrosesan bahasa alami (NLP).

---

## 🔴 Latar Belakang & Permasalahan Nyata (Riil)

Korupsi dan inefisiensi anggaran daerah masih menjadi masalah sistemik di Indonesia:
* **Dugaan Korupsi APBD Surabaya (Sept 2025):** Aksi Solidaritas Pemuda-Mahasiswa Merah Putih (SPM-MP) Jawa Timur menyoroti sederet pos belanja janggal dalam APBD Surabaya 2025, termasuk *mark-up* perjalanan dinas yang melebihi standar Kemenkeu dan pengelolaan utang daerah berbunga tinggi.
* **Tren Korupsi Canggih:** Laporan KPK mencatat lebih dari 70 kepala daerah/pejabat publik terjaring OTT (2023–2025) menggunakan modus yang semakin sulit dilacak secara manual, seperti perusahaan fiktif dan manipulasi dokumen elektronik.

## 🟡 Celah Inovasi (Unik & Belum Terselesaikan)

* **Ego Sektoral & Kebijakan Tanpa Data:** Tantangan *Smart City* di Indonesia bukan sekadar kurangnya talenta digital, melainkan mentalitas birokrasi. Kebijakan sering kali diambil berdasarkan tekanan politik, bukan berbasis data (*data-driven*).
* **Krisis Kepercayaan Warga:** Aplikasi layanan aduan publik sering kali hanya menjadi etalase tanpa tindak lanjut nyata, membuat masyarakat urban (khususnya di Surabaya) skeptis terhadap jargon *Smart City*.
* **Gap Teknologi:** Belum ada sistem analitik terpusat (*Lakehouse*) yang mampu melakukan *crawling*, integrasi, dan deteksi anomali pada data publik APBD lintas instansi secara *real-time*.

---

## 🟢 Arsitektur Solusi & Teknologi (Berdampak & Inovatif)

Sistem ini memadukan berbagai sumber data heterogen ke dalam satu *pipeline* Arsitektur Medallion (*Bronze-Silver-Gold*):

### 1. Data Sources (Sumber Data)
* **Primer:** Data tabular APBD via *scraping* SIPD/Portal Daerah dan sinyal sentimen sosial dari API Twitter/X.
* **Sekunder:** Ekstraksi teks dari PDF Laporan Hasil Pemeriksaan (LHP) BPK & KPK, serta *scraping* portal berita (NewsAPI).

### 2. Lakehouse Stack (Pemrosesan Inti)
* **Ingestion:** Apache Kafka (Disimulasikan secara *batch* untuk MVP).
* **Storage & Processing:** Apache Spark & Delta Lake (atau Apache Iceberg) untuk menangani arsitektur Medallion secara *ACID-compliant*.

### 3. Analytics & Machine Learning
* **Anomaly Detection:** Menggunakan algoritma *Machine Learning* (seperti *Isolation Forest*) untuk melacak *mark-up* anggaran atau pos belanja fiktif.
* **NLP (Natural Language Processing):** Model *IndoBERT* untuk menganalisis sentimen berita dan keluhan media sosial terkait realisasi anggaran kota.
* **Graph Analysis:** Memetakan pola aliran dana dan relasi antar-entitas (vendor vs instansi) guna mendeteksi konflik kepentingan.

### 4. Output Layer
* **Smart Dashboard:** Antarmuka interaktif berbasis **Streamlit** yang menyajikan *heatmap* anomali per kota/kecamatan, *time-series* realisasi anggaran, dan monitor sentimen publik.

---

## 🎓 Nilai Keunggulan Akademik

Proyek *Final Project* Big Data & Lakehouse ini memiliki justifikasi teknis dan sosial yang kuat:
1. **Relevan & Berani:** Menyentuh isu tata kelola nyata yang sedang hangat di masyarakat (merespons demonstrasi mahasiswa Sept 2025).
2. **Konteks Smart City Ekstrem:** Memperkuat pilar *Smart Governance*, yang merupakan fondasi terpenting sebelum membangun dimensi fisik kota cerdas.
3. **Multi-Source Data:** Menggabungkan data primer terstruktur (API SIPD) dengan data sekunder tidak terstruktur (PDF, Teks Media Sosial).
4. **Tech-Stack Industri:** Menggunakan ekosistem Big Data modern secara komprehensif (Kafka, Spark, Delta Lake, NLP, ML).
5. **Dampak Sosial (Civic Tech):** Merupakan purwarupa alat kontrol sosial berbasis data bagi publik dan aparat penegak hukum.

---

## 👥 Tim Pengembang (Institut Teknologi Sepuluh Nopember)

Pengembangan sistem didistribusikan secara paralel untuk mencapai target rilis MVP pada **Week 16**:

* **Rayhan Agnan Kusuma** - *Cloud Architect & Dashboard Designer*
* **Adel** - *Data Ingestion & Streaming Engineer*
* **Dimas** - *Lakehouse & Spark Engineer*
* **Raya** - *Machine Learning & Graph Engineer*
* **Asya** - *NLP Data Scientist*

## 👥 Pembagian Peran & Tanggung Jawab Tim

Proyek **SmartBudget** dikembangkan secara paralel oleh tim yang terdiri dari 5 spesialis. Berikut adalah struktur pembagian tugas dan tumpukan teknologi (*tech stack*) yang digunakan untuk mengejar target rilis MVP:

### 1. Cloud Architect & Dashboard Designer
* **PIC:** Rayhan
* **Fokus:** Infrastruktur *cloud* dan hasil akhir antarmuka pengguna (*end-user experience*).
* **Tanggung Jawab:** Melakukan *deployment* klaster pendukung, mengatur konektivitas antar-layanan, dan membangun dasbor SmartBudget yang interaktif.
* **Tech Stack:** AWS / GCP, Docker/Kubernetes, Apache Superset / Grafana, dan desain UI/UX.

### 2. Data Ingestion & Streaming Engineer
* **PIC:** Adel
* **Fokus:** Garda terdepan untuk menyedot (*scrape*) dan mengalirkan data mentah.
* **Tanggung Jawab:** Membuat skrip *scraper* untuk mengambil data anggaran dari portal SIPD/daerah, mengunduh PDF laporan BPK, dan menarik data Twitter/berita via API. Memastikan aliran data tidak terputus.
* **Tech Stack:** Python (Scrapy, Selenium, BeautifulSoup), REST API, Apache Kafka, dan Apache Airflow (untuk penjadwalan).

### 3. Lakehouse & Spark Engineer
* **PIC:** Dimas
* **Fokus:** Jantung pemrosesan data (Arsitektur Medallion) agar komputasinya efisien.
* **Tanggung Jawab:** Merancang skema tabel *Bronze* (mentah), *Silver* (dibersihkan), dan *Gold* (agregat siap analitik). Melakukan *join* antara data tabel SIPD dengan data sentimen publik secara terdistribusi.
* **Tech Stack:** Apache Spark (PySpark / Scala), Delta Lake atau Apache Iceberg, dan SQL.

### 4. Machine Learning & Graph Engineer
* **PIC:** Raya
* **Fokus:** "Detektif angka" untuk menemukan anomali anggaran dan aliran dana.
* **Tanggung Jawab:** Menerapkan algoritma deteksi anomali pada nilai-nilai pos belanja APBD dan membangun model graf untuk mendeteksi hubungan mencurigakan antar entitas (misal: vendor dengan alamat yang sama).
* **Tech Stack:** Scikit-Learn (Isolation Forest, Benford’s Law), Neo4j (Graph Database), dan Pandas.

### 5. NLP (Natural Language Processing) Data Scientist
* **PIC:** Asya
* **Fokus:** Membongkar data yang tidak terstruktur (teks) menjadi sinyal yang bermakna.
* **Tanggung Jawab:** Mengekstrak teks dari dokumen PDF (Laporan BPK), melakukan analisis sentimen dari cuitan warga/berita, dan mengekstrak entitas (Nama Pejabat, Dinas, Lokasi) dari teks menggunakan model bahasa.
* **Tech Stack:** IndoBERT, Hugging Face Transformers, NLTK/Spacy, dan perangkat OCR (Tesseract) untuk PDF.