import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import re

def load_and_prepare_data():
    """Mardin_temiz.csv'den veriyi yükle ve review_title'a göre gerçek etiketleri oluştur"""
    
    print("Mardin_temiz.csv dosyası yükleniyor...")
    df = pd.read_csv("Mardin_temiz.csv")
    
    print(f"Toplam yorum sayısı: {len(df)}")
    print(f"Kolonlar: {list(df.columns)}")
    
    # Review title'a göre gerçek sentiment etiketleri oluştur
    def title_to_sentiment(title):
        title_lower = title.lower()
        
        # Pozitif kelimeler
        pozitif_kelimeler = [
            'efsaneydi', 'mükemmel', 'harika', 'süper', 'lezzetli', 'güzel', 
            'muhteşem', 'tavsiye', 'öneririm', 'beğendim', 'memnun', 'iyi',
            'güzel', 'hoş', 'keyifli', 'başarılı', 'kaliteli', 'temiz'
        ]
        
        # Negatif kelimeler  
        negatif_kelimeler = [
            'kötü', 'berbat', 'rezalet', 'kötü', 'kötü', 'kötü', 'kötü',
            'vasat', 'kötü', 'kötü', 'kötü', 'kötü', 'kötü', 'kötü',
            'kötü', 'kötü', 'kötü', 'kötü', 'kötü', 'kötü', 'kötü'
        ]
        
        # Kontrol et
        for kelime in pozitif_kelimeler:
            if kelime in title_lower:
                return 'pozitif'
        
        for kelime in negatif_kelimeler:
            if kelime in title_lower:
                return 'negatif'
        
        # Özel durumlar
        if any(word in title_lower for word in ['en kotu', 'en kötü', 'kötü deneyim']):
            return 'negatif'
        if any(word in title_lower for word in ['efsaneydi', 'mükemmel', 'harika']):
            return 'pozitif'
        if any(word in title_lower for word in ['vasat', 'ortalama', 'normal']):
            return 'negatif'
        
        return 'nötr'
    
    df['gercek_sentiment'] = df['review_title'].apply(title_to_sentiment)
    
    print(f"\nGerçek sentiment dağılımı:")
    sentiment_counts = df['gercek_sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment}: {count} yorum")
    
    # Örnekler göster
    print(f"\nÖrnek review title'lar:")
    for sentiment in ['pozitif', 'negatif', 'nötr']:
        examples = df[df['gercek_sentiment'] == sentiment]['review_title'].head(3).tolist()
        print(f"{sentiment.capitalize()}: {examples}")
    
    return df

def run_bert_on_sample(df, sample_size=1000):
    """Örnek veri üzerinde BERT modelini çalıştır"""
    
    print(f"\nBERT modeli {sample_size} yorum üzerinde çalıştırılıyor...")
    
    # Örnek veri al
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    # Model1.py'deki BERT modelini kullan
    import os
    import sys
    import warnings
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        pipeline
    )
    
    # Model ayarları
    MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
    
    # GPU kontrolü
    use_gpu = torch.cuda.is_available()
    device = 0 if use_gpu else -1
    print(f"GPU aktif mi? {use_gpu}")
    
    # Model yükle
    print("Model yükleniyor...")
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if use_gpu else torch.float32
    )
    if use_gpu:
        model = model.to("cuda")
    
    clf = pipeline(
        task="sentiment-analysis",
        model=model,
        tokenizer=tok,
        device=device,
        truncation=True
    )
    
    # Metinleri birleştir
    sample_df['text'] = (sample_df['review_title'].fillna("") + " " + 
                        sample_df['clean_review'].fillna("")).str.strip()
    
    # Boş metinleri temizle
    sample_df = sample_df[sample_df['text'].astype(str).str.len() > 0].copy()
    
    # Tahmin yap
    print("Sentiment analizi yapılıyor...")
    predictions = []
    
    for text in sample_df['text']:
        try:
            result = clf(text)
            predictions.append(result[0]['label'])
        except Exception as e:
            predictions.append('3 stars')  # Hata durumunda varsayılan
    
    # BERT sonuçlarını sentiment'e çevir
    def bert_to_sentiment(bert_label):
        stars = int(bert_label.split()[0])
        if stars >= 4:
            return 'pozitif'
        elif stars == 3:
            return 'nötr'
        else:
            return 'negatif'
    
    sample_df['bert_sentiment'] = [bert_to_sentiment(pred) for pred in predictions]
    
    return sample_df

def calculate_real_accuracy(df_with_predictions):
    """Gerçek accuracy hesapla"""
    
    print("\n=== GERÇEK ACCURACY SONUÇLARI ===")
    
    # Genel accuracy
    accuracy = accuracy_score(df_with_predictions['gercek_sentiment'], 
                            df_with_predictions['bert_sentiment'])
    print(f"Genel Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Detaylı rapor
    print("\nDetaylı Sınıflandırma Raporu:")
    report = classification_report(df_with_predictions['gercek_sentiment'], 
                                 df_with_predictions['bert_sentiment'])
    print(report)
    
    # Confusion matrix
    cm = confusion_matrix(df_with_predictions['gercek_sentiment'], 
                         df_with_predictions['bert_sentiment'])
    
    print("\nConfusion Matrix:")
    print("Gerçek \\ Tahmin    Pozitif  Nötr  Negatif")
    print("Pozitif            ", cm[0] if len(cm) > 0 else "N/A")
    if len(cm) > 1:
        print("Nötr              ", cm[1])
    if len(cm) > 2:
        print("Negatif           ", cm[2])
    
    return accuracy, report, cm

def main():
    print("=== GERÇEK ACCURACY HESAPLAMA (Mardin_temiz.csv) ===\n")
    
    # Veriyi yükle
    df = load_and_prepare_data()
    
    # BERT modelini çalıştır (örnek veri üzerinde)
    sample_size = 500  # Hızlı test için
    df_with_predictions = run_bert_on_sample(df, sample_size)
    
    # Accuracy hesapla
    accuracy, report, cm = calculate_real_accuracy(df_with_predictions)
    
    # Sonuçları kaydet
    df_with_predictions.to_csv('accuracy_test_temiz_sonuclari.csv', index=False)
    print("\nTest sonuçları 'accuracy_test_temiz_sonuclari.csv' dosyasına kaydedildi.")
    
    # Özet
    print(f"\n=== ÖZET ===")
    print(f"Test edilen yorum sayısı: {len(df_with_predictions)}")
    print(f"BERT Modeli Gerçek Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    if accuracy > 0.8:
        print("🎉 Mükemmel! Model çok iyi çalışıyor!")
    elif accuracy > 0.7:
        print("👍 İyi! Model kabul edilebilir seviyede.")
    elif accuracy > 0.6:
        print("⚠️ Orta! Model iyileştirilebilir.")
    else:
        print("❌ Düşük! Model iyileştirme gerektiriyor.")

if __name__ == "__main__":
    main()

