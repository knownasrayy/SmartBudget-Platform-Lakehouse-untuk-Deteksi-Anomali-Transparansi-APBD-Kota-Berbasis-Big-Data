# 🏗️ Arsitektur & Infrastruktur SmartBudget Lakehouse

Dokumen ini menjelaskan secara rinci desain infrastruktur, teknologi yang digunakan, serta alur data (*data pipeline*) pada platform **SmartBudget Lakehouse**. Platform ini dibangun menggunakan ekosistem *Big Data* untuk mensimulasikan lingkungan kelas *Enterprise*, secara khusus didesain untuk mendeteksi anomali pada APBD secara transparan.

---

## 1. 🏛️ Konsep Utama: Medallion Data Lakehouse Architecture

Sistem ini mengadopsi pola arsitektur **Medallion**, yang membagi siklus data menjadi tiga lapisan (zona) utama untuk memastikan kualitas, integritas, dan performa tinggi saat pemrosesan analitik berskala besar.

### 🥉 Bronze Layer (Raw Ingestion Layer)
- **Tujuan**: Menampung data mentah (*raw data*) seperti apa adanya dari berbagai sumber tanpa transformasi yang merubah esensi data.
- **Implementasi**: Sesuai dengan spesifikasi, data menggunakan simulasi/generate (*data primer dummy*) sebagai simulasi tarikan langsung dari API (seperti CKAN portal open data kota). Data ini disimpan dalam bentuk aslinya (CSV) di dalam direktori `data/bronze/`.
- **Komponen Kunci**: Script Python `generate_apbd_synthetic.py` digunakan untuk secara dinamis membuat dataset transaksi pemerintahan.

### 🥈 Silver Layer (Cleansing & Conforming)
- **Tujuan**: Membersihkan, menyaring, dan menyelaraskan (*conforming*) data yang kotor dari *Bronze layer*.
- **Proses yang Terjadi**:
  - Penanganan nilai kosong (*Null/NaN handling*).
  - Standardisasi format string dan angka (menghapus simbol mata uang).
  - Transformasi *casting* tipe data menjadi tipe yang tepat.
- **Teknologi Utama**: **PySpark** digunakan untuk membaca data dari Bronze, memproses secara paralel/terdistribusi, dan menyimpan hasilnya dalam format **Delta Lake** di direktori `data/silver/`. Format Delta Lake memberikan jaminan ACID (*Atomicity, Consistency, Isolation, Durability*), sehingga mencegah korupsi data.

### 🥇 Gold Layer (Analytics & Machine Learning)
- **Tujuan**: Menyediakan data final yang sudah diagregasi, diprediksi, dan siap disajikan (*business-ready data*) ke *dashboard* aplikasi frontend.
- **Proses yang Terjadi**:
  - **Deteksi Anomali (MLlib)**: Menggunakan algoritma **K-Means Clustering** untuk menghitung jarak Euclidean (*Anomaly Score*) dari masing-masing paket pengadaan, sehingga indikasi anomali anggaran yang mencurigakan terdeteksi secara statistik.
  - Agregasi data ringkasan per dinas pemerintahan (SKPD) untuk indikator dashboard.
- **Implementasi**: Proses *Machine Learning* ini dieksekusi oleh `anomaly_detector.py` yang memproduksi file siap konsumsi (`gold_anomaly_transactions.csv` & `gold_skpd_summary.csv`) di zona Gold.

---

## 2. ⚙️ Stack Teknologi Infrastruktur

Platform ini difokuskan pada pemrosesan volume data tinggi sehingga memanfaatkan utilitas standar industri *Big Data*:

| Komponen | Teknologi | Peran |
| :--- | :--- | :--- |
| **Data Processing Engine** | **Apache Spark (PySpark)** | *Engine* pemrosesan data terdistribusi (*large-scale data processing*). Digunakan penuh di layer Silver dan Gold. |
| **Storage Layer** | **Delta Lake** | Lapisan penyimpanan berbasis file dengan keunggulan transaksi ACID, performa *time travel*, dan metadata dinamis. |
| **Machine Learning** | **Spark MLlib** | *Library Machine Learning* terdistribusi bawaan dari Spark. Sangat cocok untuk *Clustering* anomali dengan dataset jutaan baris. |
| **Backend API & Serving** | **FastAPI (Python)** | Framework modern berkecepatan tinggi yang menyajikan data layer Gold dalam bentuk **REST API** (`/api/anomalies`) ke Frontend. |
| **Frontend Dashboard** | **Vanilla JS, Tailwind CSS** | User Interface interaktif untuk visualisasi dan transparansi data anomali secara *real-time*. |

---

## 3. 🔄 Alur Pipa Data (Data Pipeline Flow)

Berikut adalah siklus aliran data dari hulu ke hilir:

1. **Data Generation (Ingestion Simulasi)**
   - Script: `src/ml_engine/data_generator/generate_apbd_synthetic.py`
   - Data dummy pengadaan dan SKPD di-*generate* kemudian disimpan sebagai CSV pada direktori `data/bronze/`.
2. **Transformasi Silver (Cleansing)**
   - Script: `src/lakehouse/silver_transform.py`
   - Pekerja PySpark melakukan *cleaning* (menyesuaikan format Pagu Anggaran) lalu menulis *dataframe* ke `data/silver/` menggunakan format *Delta Lake*.
3. **Spark MLlib Anomaly Scoring (Transformasi Gold)**
   - Script: `src/ml_engine/anomaly_detector.py`
   - PySpark membaca data bersih dari *Silver layer*.
   - Menerapkan rekayasa fitur (*Feature Engineering*) via VectorAssembler & StandardScaler.
   - Memasukkan fitur ke model **K-Means**, menghitung Euclidean Distance, lalu menyematkan *Anomaly Score* per baris.
   - Menyimpan *Scored Data* ke `data/gold/`.
4. **Data Serving (FastAPI Backend)**
   - Script: `src/api/main.py`
   - Server membaca file Gold, membungkusnya dengan JSON payload, kemudian menyediakan *endpoint* REST untuk dikonsumsi frontend.
5. **Client Dashboard Consumption**
   - Web App mengambil data melalui AJAX API Request dan merender status *WARNING* untuk anomali pada tabel dan peta secara dinamis.

---

## 4. 💻 Operasional & Lingkungan Lokal (Windows)

Untuk menjembatani ekosistem Big Data (yang idealnya berjalan di server UNIX) ke *environment* pengembangan Windows lokal, berikut adalah arsitektur pendukungnya:

- **Hadoop Winutils**: *Binary file* (`winutils.exe`) diperlukan di environment Windows agar Apache Spark dapat meniru *filesystem* HDFS untuk menulis output data tanpa gagal akses direktori.
- **Environment Variables**: Bergantung erat pada definisi *path* dari `JAVA_HOME`, `SPARK_HOME`, dan `HADOOP_HOME`.
- **PowerShell Wrapper**: Pemanggilan PySpark dibungkus melalui *script* pembantu `run_pyspark.ps1` untuk memastikan kelancaran alokasi memori JVM dan *compatibility arguments*.

### 🚀 Menjalankan Pipeline Lengkap (Run-book)
Gunakan *Command Prompt* atau PowerShell dari root folder untuk memicu alur secara sekuensial:

```powershell
# 1. Bangkitkan Data (Simulasi Bronze)
python src/ml_engine/data_generator/generate_apbd_synthetic.py

# 2. Proses Transformasi ke Silver Layer
.\run_pyspark.ps1 src\lakehouse\silver_transform.py

# 3. Proses Penilaian Anomali (Machine Learning) ke Gold Layer
.\run_pyspark.ps1 src\ml_engine\anomaly_detector.py

# 4. Angkat Server Backend & Frontend Dashboard
python run_server.py
```
*(Setelah poin ke-4 dijalankan, Anda dapat melihat hasilnya pada `http://localhost:8080`)*
