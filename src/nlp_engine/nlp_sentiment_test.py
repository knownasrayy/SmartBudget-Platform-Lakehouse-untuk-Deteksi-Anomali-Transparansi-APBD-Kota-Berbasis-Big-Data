import pandas as pd
from transformers import pipeline
import os

print("Loading model...")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="w11wo/indonesian-roberta-base-sentiment-classifier"
)

INPUT_PATH = "data/bronze/tweets_berita_raw.csv"
OUTPUT_PATH = "data/gold/sentiment_results.csv"

print(f"Membaca data dari {INPUT_PATH}...")
df = pd.read_csv(INPUT_PATH)
print(f"Total baris: {len(df)}")

def classify(text):
    result = sentiment_pipeline(str(text), truncation=True)[0]
    return pd.Series([result['label'], result['score']])

print("Memproses sentiment analysis...")
df[['Sentimen', 'Confidence']] = df['teks'].apply(classify)

# --- Keyword-based flagging ---
keywords_red_flag = [
    "korupsi", "markup", "dugaan", "temuan", "janggal",
    "ketidaksesuaian", "demo", "menuding", "mengendus", "tangkap"
]

def flag_keyword(text):
    text_lower = str(text).lower()
    return any(kw in text_lower for kw in keywords_red_flag)

print("Menambahkan keyword flagging...")
df['flag_anomali_keyword'] = df['teks'].apply(flag_keyword)

os.makedirs("data/gold", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"Selesai. Output disimpan di {OUTPUT_PATH}")
print(df[['id', 'teks', 'Sentimen', 'Confidence', 'flag_anomali_keyword']])