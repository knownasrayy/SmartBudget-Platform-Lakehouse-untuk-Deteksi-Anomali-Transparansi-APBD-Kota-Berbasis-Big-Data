#!/bin/bash
# run_ingestion.sh
# Skrip otomasi untuk menjalankan proses data ingestion secara berkala

echo "==========================================="
echo "Mulai Eksekusi Data Ingestion SmartBudget"
echo "Waktu: $(date)"
echo "==========================================="

# Arahkan ke root direktori proyek
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Opsional: Aktifkan virtual environment jika ada
if [ -d ".venv" ]; then
    echo "Mengaktifkan virtual environment..."
    source .venv/Scripts/activate || source .venv/bin/activate
fi

# Jalankan skrip Python
echo "Menjalankan skrip src/ingestion/ingest_apbd.py (Open Data Surabaya)..."
python src/ingestion/ingest_apbd.py

echo "Menjalankan skrip src/ingestion/ingest_lpse.py (Data LPSE/LKPP)..."
python src/ingestion/ingest_lpse.py

echo "Menjalankan skrip src/ingestion/ingest_news_twitter.py (Data Opini Publik)..."
python src/ingestion/ingest_news_twitter.py

echo "Menjalankan skrip src/nlp_engine/nlp_sentiment.py (Pemrosesan NLP Sentimen)..."
python src/nlp_engine/nlp_sentiment.py

echo "Eksekusi selesai pada: $(date)"
echo "==========================================="
