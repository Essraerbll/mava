import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import numpy as np

print("=== MARDİN RESTAURANT TÜRKÇE SENTİMENT ANALİZİ ===\n")

# Temizlenmiş veriyi oku
df = pd.read_csv('Mardin_temiz.csv')
print(f"📊 Veri yüklendi: {len(df):,} yorum, {df['restaurant_name'].nunique()} restoran")

# GPU kontrolü
use_gpu = torch.cuda.is_available()
device = 0 if use_gpu else -1
print(f"🚀 GPU: {use_gpu} | Device: {device}")

# Daha basit sentiment modeli yükle
print("\n🤖 Sentiment modeli yükleniyor...")
MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"  # 1-5 yıldız

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if use_gpu else torch.float32
    )
    
    if use_gpu:
        model = model.to("cuda")
    
    print("✅ Sentiment modeli yüklendi!")
    
except Exception as e:
    print(f"❌ Model yüklenemedi: {e}")
    exit(1)

# Pipeline oluştur
clf = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    device=device,
    truncation=True,
    max_length=512
)

print(f"\n📝 Sentiment analizi başlıyor...")

# Batch işleme
BATCH_SIZE = 32 if use_gpu else 16
predictions = []
scores = []

for i in range(0, len(df), BATCH_SIZE):
    batch_texts = df['clean_review'].iloc[i:i+BATCH_SIZE].tolist()
    
    try:
        results = clf(batch_texts)
        
        for result in results:
            # Label'ı sentiment'e çevir (1-5 yıldız)
            label = result['label']
            stars = int(label.split()[0])  # "1 star" -> 1
            
            if stars <= 2:
                pred = 'negatif'
            elif stars == 3:
                pred = 'nötr'
            else:
                pred = 'pozitif'
            
            predictions.append(pred)
            scores.append(result['score'])
            
    except Exception as e:
        print(f"❌ Batch {i//BATCH_SIZE + 1} hatası: {e}")
        # Hata durumunda varsayılan değer
        for _ in range(len(batch_texts)):
            predictions.append('nötr')
            scores.append(0.5)

print(f"✅ Sentiment analizi tamamlandı!")

# Sonuçları DataFrame'e ekle
df['sentiment'] = predictions
df['sentiment_score'] = scores

# Restoran bazında özet
print(f"\n📊 RESTORAN BAZINDA SONUÇLAR:")
agg = df.groupby('restaurant_name')['sentiment'].value_counts().unstack(fill_value=0)

# Eksik sütunları ekle
for col in ['negatif', 'nötr', 'pozitif']:
    if col not in agg.columns:
        agg[col] = 0

agg['toplam'] = agg[['negatif', 'nötr', 'pozitif']].sum(axis=1)
agg['pozitif_%'] = (agg['pozitif'] / agg['toplam'] * 100).round(1)
agg['negatif_%'] = (agg['negatif'] / agg['toplam'] * 100).round(1)

# Sırala
agg = agg.sort_values(['pozitif_%', 'toplam'], ascending=[False, False])

# Sonuçları kaydet
output_file = 'Mardin_turkce_sentiment.csv'
agg.to_csv(output_file)
print(f"💾 Sonuçlar kaydedildi: {output_file}")

# En iyi 10 restoran
print(f"\n🏆 EN İYİ 10 RESTORAN (5+ yorum):")
top_restaurants = agg[agg['toplam'] >= 5].head(10)
for i, (name, row) in enumerate(top_restaurants.iterrows(), 1):
    print(f"{i:2d}. {name[:40]:<40} | Pozitif: {row['pozitif_%']:>5.1f}% | Toplam: {int(row['toplam']):>3d}")

print(f"\n✅ TÜRKÇE SENTİMENT ANALİZİ TAMAMLANDI!")
print(f"Toplam {len(df):,} yorum analiz edildi")
print(f"En iyi restoran: {top_restaurants.index[0]} ({top_restaurants.iloc[0]['pozitif_%']:.1f}% pozitif)")
