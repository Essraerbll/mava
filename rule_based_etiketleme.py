import pandas as pd
import re
import numpy as np
from collections import Counter

print("=== MARDİN RESTAURANT RULE-BASED OTOMATİK ETİKETLEME ===\n")

# Temizlenmiş veriyi oku
df = pd.read_csv('Mardin_temiz.csv')
total_reviews = len(df)

print(f"📊 TOPLAM: {total_reviews:,} yorum")
print(f"🏪 RESTORAN: {df['restaurant_name'].nunique()} adet")

# Türkçe sentiment anahtar kelimeleri
print(f"\n🔑 SENTIMENT ANAHTAR KELİMELERİ YÜKLENİYOR...")

positive_words = [
    # Yemek kalitesi
    'güzel', 'lezzetli', 'harika', 'mükemmel', 'efsane', 'muhteşem', 'süper',
    'çok iyi', 'çok güzel', 'çok lezzetli', 'doyurucu', 'taze', 'kaliteli',
    'özel', 'yöresel', 'geleneksel', 'ev yapımı', 'tadı damağımda',
    
    # Hizmet
    'hızlı', 'sıcak', 'dostane', 'güler yüzlü', 'profesyonel', 'dikkatli',
    'temiz', 'düzenli', 'rahat', 'ferah', 'atmosfer', 'ambiyans',
    
    # Genel pozitif
    'beğendim', 'tavsiye ederim', 'tekrar gelirim', 'memnun kaldım',
    'değer', 'uygun fiyat', 'kaliteli', 'öneririm', 'başarılı'
]

negative_words = [
    # Yemek kalitesi
    'kötü', 'berbat', 'lezzetsiz', 'bayat', 'soğuk', 'sıcak değil',
    'çok kötü', 'çok berbat', 'tatsız', 'yavan', 'kuru', 'sert',
    'çiğ', 'yanık', 'bayat', 'bozuk', 'kokuşmuş',
    
    # Hizmet
    'yavaş', 'soğuk', 'kaba', 'ilgisiz', 'dikkatsiz', 'kirli',
    'düzensiz', 'gürültülü', 'kalabalık', 'sıkışık', 'rahatsız',
    
    # Genel negatif
    'beğenmedim', 'tavsiye etmem', 'tekrar gelmem', 'memnun kalmadım',
    'pahalı', 'değmez', 'kötü deneyim', 'hayal kırıklığı', 'berbat'
]

neutral_words = [
    'orta', 'normal', 'standart', 'sıradan', 'alışılmış', 'beklenen',
    'fiyat performans', 'uygun', 'kabul edilebilir', 'şöyle böyle',
    'ne iyi ne kötü', 'kararsız', 'bilgi', 'sadece', 'sade'
]

print(f"✅ Pozitif kelimeler: {len(positive_words)} adet")
print(f"✅ Negatif kelimeler: {len(negative_words)} adet")
print(f"✅ Nötr kelimeler: {len(neutral_words)} adet")

# Etiketleme fonksiyonu
def rule_based_sentiment(text):
    if pd.isna(text):
        return 'nötr', 0.0
    
    text = text.lower()
    
    # Kelime sayılarını hesapla
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    neu_count = sum(1 for word in neutral_words if word in text)
    
    # Toplam kelime sayısı
    total_words = len(text.split())
    
    # Sentiment skorları
    pos_score = pos_count / max(total_words, 1)
    neg_score = neg_count / max(total_words, 1)
    neu_score = neu_count / max(total_words, 1)
    
    # En yüksek skoru bul
    scores = {'pozitif': pos_score, 'negatif': neg_score, 'nötr': neu_score}
    max_sentiment = max(scores, key=scores.get)
    max_score = scores[max_sentiment]
    
    # Güven skoru hesapla
    confidence = max_score * 100
    
    # Eğer hiç anahtar kelime yoksa nötr
    if pos_count == 0 and neg_count == 0 and neu_count == 0:
        return 'nötr', 0.0
    
    return max_sentiment, confidence

print(f"\n🚀 OTOMATİK ETİKETLEME BAŞLIYOR...")

# Her yorumu etiketle
predictions = []
confidences = []
sentiment_scores = []

for i, row in df.iterrows():
    if i % 100 == 0:
        print(f"📝 İşleniyor: {i+1}/{total_reviews} ({((i+1)/total_reviews*100):.1f}%)")
    
    sentiment, confidence = rule_based_sentiment(row['clean_review'])
    predictions.append(sentiment)
    confidences.append(confidence)
    
    # Sentiment skoru (pozitif: 1, nötr: 0.5, negatif: 0)
    if sentiment == 'pozitif':
        sentiment_scores.append(1.0)
    elif sentiment == 'negatif':
        sentiment_scores.append(0.0)
    else:
        sentiment_scores.append(0.5)

print(f"✅ Otomatik etiketleme tamamlandı!")

# Sonuçları DataFrame'e ekle
df['rule_based_sentiment'] = predictions
df['confidence_score'] = confidences
df['sentiment_numeric'] = sentiment_scores

# İstatistikler
print(f"\n📊 ETİKETLEME SONUÇLARI:")
sentiment_counts = Counter(predictions)
for sentiment, count in sentiment_counts.items():
    percentage = (count / total_reviews) * 100
    print(f"{sentiment.capitalize()}: {count:,} yorum ({percentage:.1f}%)")

# Güven skoru analizi
print(f"\n🎯 GÜVEN SKORU ANALİZİ:")
print(f"Ortalama güven: {np.mean(confidences):.1f}%")
print(f"En yüksek güven: {np.max(confidences):.1f}%")
print(f"En düşük güven: {np.min(confidences):.1f}%")

# Düşük güvenli yorumları bul (manuel kontrol için)
low_confidence_threshold = 20  # %20'den düşük güven
low_confidence_mask = df['confidence_score'] < low_confidence_threshold
low_confidence_count = low_confidence_mask.sum()

print(f"\n⚠️ MANUEL KONTROL GEREKEN YORUMLAR:")
print(f"Güven skoru < %{low_confidence_threshold}: {low_confidence_count:,} yorum")
print(f"Manuel kontrol oranı: {(low_confidence_count/total_reviews*100):.1f}%")

# Restoran bazında özet
print(f"\n📈 RESTORAN BAZINDA SONUÇLAR:")
agg = df.groupby('restaurant_name')['rule_based_sentiment'].value_counts().unstack(fill_value=0)

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
output_file = 'Mardin_rule_based_sentiment.csv'
agg.to_csv(output_file)
print(f"💾 Sonuçlar kaydedildi: {output_file}")

# En iyi 10 restoran
print(f"\n🏆 EN İYİ 10 RESTORAN (5+ yorum):")
top_restaurants = agg[agg['toplam'] >= 5].head(10)
for i, (name, row) in enumerate(top_restaurants.iterrows(), 1):
    print(f"{i:2d}. {name[:40]:<40} | Pozitif: {row['pozitif_%']:>5.1f}% | Toplam: {int(row['toplam']):>3d}")

# Düşük güvenli yorumları ayrı dosyaya kaydet
if low_confidence_count > 0:
    low_confidence_df = df[low_confidence_mask][['restaurant_name', 'clean_review', 'confidence_score']]
    low_confidence_file = 'manuel_kontrol_gereken_yorumlar.csv'
    low_confidence_df.to_csv(low_confidence_file, index=False)
    print(f"\n📋 Manuel kontrol gereken yorumlar: {low_confidence_file}")

print(f"\n✅ RULE-BASED ETİKETLEME TAMAMLANDI!")
print(f"🎯 Sonraki adım: Düşük güvenli yorumları manuel kontrol et")
print(f"🚀 Sonra: Model eğitimi!")
