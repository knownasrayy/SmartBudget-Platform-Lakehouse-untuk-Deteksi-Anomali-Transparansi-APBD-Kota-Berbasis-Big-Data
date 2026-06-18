import os
import glob
import json
import pandas as pd
from transformers import pipeline
from pathlib import Path

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def run_sentiment_pipeline():
    BASE = Path(__file__).resolve().parents[2]
    print("=== NLP Engine: Sentiment Analysis (IndoBERT) ===")
    
    bronze_dir = BASE / "data/bronze"
    all_data = []

    # 1. Baca YouTube Comments (yt_comments_raw.json)
    yt_file = bronze_dir / "yt_comments_raw.json"
    if yt_file.exists():
        try:
            with open(yt_file, 'r', encoding='utf-8') as f:
                yt_data = json.load(f)
                for item in yt_data:
                    all_data.append({
                        'teks': item.get('textOriginal', ''),
                        'sumber': f"YouTube ({item.get('authorDisplayName', 'Unknown')})",
                        'tanggal': item.get('publishedAt', '')
                    })
            print(f"[NLP] Berhasil membaca {len(yt_data)} komentar dari YouTube.")
        except Exception as e:
            print(f"[NLP] Gagal membaca {yt_file}: {e}")

    # 2. Baca GNews (gnews_raw.csv)
    gnews_file = bronze_dir / "gnews_raw.csv"
    if gnews_file.exists():
        try:
            df_gnews = pd.read_csv(gnews_file)
            for _, row in df_gnews.iterrows():
                teks_gabungan = f"{row.get('title', '')}. {row.get('description', '')}"
                all_data.append({
                    'teks': teks_gabungan.strip(),
                    'sumber': row.get('source_name', 'Google News'),
                    'tanggal': row.get('published_at', '')
                })
            print(f"[NLP] Berhasil membaca {len(df_gnews)} artikel dari Google News.")
        except Exception as e:
            print(f"[NLP] Gagal membaca {gnews_file}: {e}")

    # 3. Baca Tweets/Berita (tweets_berita_raw_*.csv) jika ada
    tweet_pattern = str(bronze_dir / "tweets_berita_raw_*.csv")
    latest_tweet = get_latest_file(tweet_pattern)
    if latest_tweet:
        try:
            df_tweet = pd.read_csv(latest_tweet)
            for _, row in df_tweet.iterrows():
                all_data.append({
                    'teks': row.get('teks', ''),
                    'sumber': row.get('sumber', 'Twitter'),
                    'tanggal': row.get('tanggal', '')
                })
            print(f"[NLP] Berhasil membaca {len(df_tweet)} opini dari {os.path.basename(latest_tweet)}.")
        except Exception as e:
            print(f"[NLP] Gagal membaca {latest_tweet}: {e}")

    # Konversi ke DataFrame
    if not all_data:
        print("[NLP] Tidak ada data di Bronze layer untuk diproses.")
        return

    df = pd.DataFrame(all_data)
    # Hapus data kosong
    df = df[df['teks'].str.strip() != '']

    print("[NLP] Memuat model sentimen (IndoBERT/RoBERTa)...")
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="w11wo/indonesian-roberta-base-sentiment-classifier"
        )
    except Exception as e:
        print(f"[NLP] [ERROR] Gagal memuat model NLP: {e}")
        return

    print(f"[NLP] Memproses sentimen untuk {len(df)} baris data (bisa memakan waktu beberapa menit)...")
    
    def get_sentiment(text):
        try:
            # Batasi hingga 512 karakter pertama
            res = sentiment_pipeline(str(text)[:512])[0]
            return pd.Series([res['label'], res['score']])
        except:
            return pd.Series(["neutral", 0.0])

    df[['sentiment_label', 'sentiment_score']] = df['teks'].apply(get_sentiment)

    # Normalisasi Label
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
    
    # Ringkasan distribusi
    dist = df['sentiment_label'].value_counts()
    print("\n--- Ringkasan Distribusi Sentimen ---")
    for k, v in dist.items():
        print(f"{k}: {v} opini")
    print("-------------------------------------")

if __name__ == "__main__":
    run_sentiment_pipeline()
