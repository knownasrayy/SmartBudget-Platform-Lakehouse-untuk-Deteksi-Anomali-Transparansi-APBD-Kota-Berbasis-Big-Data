from transformers import pipeline, AutoTokenizer, AutoModel
import torch

print("=== Bagian 1: Load IndoBERT base model ===")
tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
model = AutoModel.from_pretrained("indobenchmark/indobert-base-p1")
print("IndoBERT base model berhasil di-load.")

sample_text = "Pipa PDAM di MERR bocor lagi, air macet total"
inputs = tokenizer(sample_text, return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)
print(f"Output shape (embedding): {outputs.last_hidden_state.shape}")

print("\n=== Bagian 2: Sentiment Classification ===")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="w11wo/indonesian-roberta-base-sentiment-classifier"
)

test_sentences = [
    "Pipa PDAM di MERR bocor lagi, air macet total",
    "Pembangunan jalan baru di Surabaya berjalan lancar dan tepat waktu",
    "Anggaran untuk perbaikan sekolah tahun ini meningkat signifikan",
    "Proyek ini terlambat dan menghabiskan dana lebih dari yang seharusnya",
    "Pelayanan di kantor kelurahan hari ini cukup memuaskan"
]

for text in test_sentences:
    result = sentiment_pipeline(text)
    print(f"Teks: {text}")
    print(f"  -> Sentimen: {result[0]['label']}, Confidence: {result[0]['score']:.4f}\n")