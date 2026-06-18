import os
import glob
import pandas as pd
from transformers import pipeline
from pathlib import Path

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return max(files, key=os.path.getctime)

def run_sentiment_pipeline():
    BASE = Path(__file__).resolve().parents[2]
    print("=== NLP Engine: Sentiment Analysis ===")
    
    try:
        bronze_pattern = str(BASE / "data/bronze/tweets_berita_raw_*.csv")
        latest_file = get_latest_file(bronze_pattern)
        print(f"[NLP] Membaca data opini publik terbaru dari Bronze Layer: {os.path.basename(latest_file)}")
        df = pd.read_csv(latest_file)
    except Exception as e:
        print(f"[NLP] [ERROR] Gagal membaca file dari Bronze Layer: {e}")
        return

    print("[NLP] Memuat model sentimen (IndoBERT/RoBERTa)...")
    try:
        # Pipeline sentimen bahasa indonesia
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="w11wo/indonesian-roberta-base-sentiment-classifier"
        )
    except Exception as e:
        print(f"[NLP] [ERROR] Gagal memuat model NLP: {e}")
        print("Harap pastikan koneksi internet stabil untuk unduh model pertama kali.")
        return

    print(f"[NLP] Memproses sentimen untuk {len(df)} baris data...")
    
    def get_sentiment(text):
        try:
            # Batasi hingga 512 karakter pertama (batas token BERT)
            res = sentiment_pipeline(str(text)[:512])[0]
            return pd.Series([res['label'], res['score']])
        except:
            return pd.Series(["neutral", 0.0])

    # Terapkan inferensi NLP
    df[['sentiment_label', 'sentiment_score']] = df['teks'].apply(get_sentiment)

    # Normalisasi Label (Sesuai kebutuhan Dasbor / UI)
    def normalize_label(label):
        label = str(label).lower()
        if "positive" in label or "positif" in label:
            return "Positif"
        elif "negative" in label or "negatif" in label:
            return "Negatif"
        else:
            return "Netral"

    df['sentiment_label'] = df['sentiment_label'].apply(normalize_label)

    # Simpan ke Gold Layer
    out_dir = BASE / "data/gold"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "sentiment_results.csv"

    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"[NLP] Selesai! Hasil sentimen (Gold Layer) disimpan ke: {out_file}")
    
    # Menampilkan ringkasan distribusi
    dist = df['sentiment_label'].value_counts()
    print("\n--- Ringkasan Distribusi Sentimen ---")
    for k, v in dist.items():
        print(f"{k}: {v} opini")
    print("-------------------------------------")

if __name__ == "__main__":
    run_sentiment_pipeline()
