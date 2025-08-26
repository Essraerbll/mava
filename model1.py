import os
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Gürültü uyarılarını kapatmak istersen:
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Daha uyumlu bir model kullanıyoruz
MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"  # TR+EN için uyumlu
CSV_IN = "Mardin.csv"                                    # dosya adını gerekirse değiştir
CSV_OUT = "restaurant_sentiment_bert_gpu.csv"

def main():
    # 1) Cihaz
    use_gpu = torch.cuda.is_available()
    device = 0 if use_gpu else -1
    print(f"GPU aktif mi? {use_gpu} | device={device}")

    # 2) Model/Tokenizer (GPU + FP16)
    print("Model yükleniyor...")
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL,
        torch_dtype=torch.float16 if use_gpu else torch.float32
    )
    if use_gpu:
        model = model.to("cuda")

    clf = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tok,
        device=device,
        truncation=True
    )

    # 3) Veriyi yükle
    print("CSV dosyası okunuyor...")
    df = pd.read_csv(CSV_IN)
    df["text"] = (df["review_title"].fillna("") + " " + df["review_text"].fillna("")).str.strip()

    # 4) Batch tahmin
    print("Sentiment analizi yapılıyor...")
    BATCH = 128 if use_gpu else 32
    preds, scores = [], []
    for i in range(0, len(df), BATCH):
        batch = df["text"].iloc[i:i+BATCH].tolist()
        out = clf(batch)
        preds.extend([o["label"] for o in out])
        scores.extend([o["score"] for o in out])

    # 5) Label eşlemesi (BERT: 1-5 yıldız)
    print("Sonuçlar işleniyor...")
    df["sentiment"] = preds
    df["sentiment_score"] = scores
    
    # Yıldız sayısını sayısal değere çevir
    df["sentiment_numeric"] = df["sentiment"].str.extract(r'(\d+)').astype(float)
    
    # 1-2 yıldız: negatif, 3: nötr, 4-5: pozitif
    def categorize_sentiment(stars):
        if stars <= 2:
            return "negatif"
        elif stars == 3:
            return "nötr"
        else:
            return "pozitif"
    
    df["sentiment_category"] = df["sentiment_numeric"].apply(categorize_sentiment)

    # 6) Restoran bazında % hesapla
    agg = (df.groupby("restaurant_name")["sentiment_category"].value_counts()
             .unstack(fill_value=0).reset_index())

    for c in ["pozitif","negatif","nötr"]:
        if c not in agg.columns: agg[c] = 0

    agg["toplam"] = agg[["pozitif","negatif","nötr"]].sum(1)
    # agg = agg[agg["toplam"] >= 5]  # Filtreyi kaldırdık - tüm restoranlar görünsün
    agg["pozitif_%"] = (agg["pozitif"]/agg["toplam"]*100).round(1)
    agg["negatif_%"] = (agg["negatif"]/agg["toplam"]*100).round(1)

    agg.sort_values(["pozitif_%","toplam"], ascending=[False, False]).to_csv(CSV_OUT, index=False)
    print("Bitti ->", CSV_OUT)
    print(f"Toplam {len(df)} yorum analiz edildi")

if __name__ == "__main__":
    try:
        main()
    except torch.cuda.OutOfMemoryError:
        # VRAM yetmezse batch küçült
        print("CUDA OOM: BATCH değerini 64/32 yapıp tekrar dene.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        print("Lütfen CSV dosyasının doğru formatta olduğundan emin olun")
