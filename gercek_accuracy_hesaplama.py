import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_prepare_data():
    """Mardin.csv'den veriyi yükle ve rating'e göre gerçek etiketleri oluştur"""
    
    print("Mardin.csv dosyası yükleniyor...")
    df = pd.read_csv("Mardin.csv")
    
    print(f"Toplam yorum sayısı: {len(df)}")
    print(f"Kolonlar: {list(df.columns)}")
    
    # Rating dağılımını göster
    print("\nRating dağılımı:")
    rating_counts = df['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        print(f"{rating} yıldız: {count} yorum")
    
    # Rating'e göre gerçek sentiment etiketleri oluştur
    def rating_to_sentiment(rating):
        if rating >= 4:
            return 'pozitif'
        elif rating == 3:
            return 'nötr'
        else:
            return 'negatif'
    
    df['gercek_sentiment'] = df['rating'].apply(rating_to_sentiment)
    
    print(f"\nGerçek sentiment dağılımı:")
    sentiment_counts = df['gercek_sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment}: {count} yorum")
    
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
                        sample_df['review_text'].fillna("")).str.strip()
    
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
    
    # Kategori bazında accuracy
    print("\nKategori Bazında Accuracy:")
    for sentiment in ['pozitif', 'nötr', 'negatif']:
        if sentiment in df_with_predictions['gercek_sentiment'].values:
            mask = df_with_predictions['gercek_sentiment'] == sentiment
            cat_accuracy = accuracy_score(
                df_with_predictions[mask]['gercek_sentiment'],
                df_with_predictions[mask]['bert_sentiment']
            )
            print(f"{sentiment.capitalize()}: {cat_accuracy:.3f} ({cat_accuracy*100:.1f}%)")
    
    return accuracy, report, cm

def create_accuracy_visualizations(df_with_predictions, accuracy, cm):
    """Accuracy görselleştirmeleri oluştur"""
    
    # 1. Accuracy grafiği
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.bar(['BERT Modeli'], [accuracy], color='#4ECDC4')
    plt.title(f'BERT Modeli Gerçek Accuracy\n{accuracy:.3f} ({accuracy*100:.1f}%)')
    plt.ylabel('Accuracy')
    plt.ylim(0, 1)
    
    # 2. Confusion matrix heatmap
    plt.subplot(1, 2, 2)
    if len(cm) > 0:
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Pozitif', 'Nötr', 'Negatif'],
                   yticklabels=['Pozitif', 'Nötr', 'Negatif'])
        plt.title('Confusion Matrix')
        plt.xlabel('Tahmin')
        plt.ylabel('Gerçek')
    
    plt.tight_layout()
    plt.savefig('gercek_accuracy_sonuclari.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Sentiment dağılımı karşılaştırması
    plt.figure(figsize=(10, 6))
    
    gercek_counts = df_with_predictions['gercek_sentiment'].value_counts()
    bert_counts = df_with_predictions['bert_sentiment'].value_counts()
    
    x = np.arange(len(gercek_counts))
    width = 0.35
    
    plt.bar(x - width/2, gercek_counts.values, width, label='Gerçek', alpha=0.8)
    plt.bar(x + width/2, bert_counts.values, width, label='BERT Tahmini', alpha=0.8)
    
    plt.xlabel('Sentiment')
    plt.ylabel('Yorum Sayısı')
    plt.title('Gerçek vs BERT Tahmini Sentiment Dağılımı')
    plt.xticks(x, gercek_counts.index)
    plt.legend()
    plt.tight_layout()
    plt.savefig('sentiment_dagilimi_karsilastirma.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    print("=== GERÇEK ACCURACY HESAPLAMA ===\n")
    
    # Veriyi yükle
    df = load_and_prepare_data()
    
    # BERT modelini çalıştır (örnek veri üzerinde)
    sample_size = 500  # Hızlı test için
    df_with_predictions = run_bert_on_sample(df, sample_size)
    
    # Accuracy hesapla
    accuracy, report, cm = calculate_real_accuracy(df_with_predictions)
    
    # Görselleştirmeler oluştur
    try:
        create_accuracy_visualizations(df_with_predictions, accuracy, cm)
        print("\nGörselleştirmeler kaydedildi.")
    except Exception as e:
        print(f"Görselleştirme hatası: {e}")
    
    # Sonuçları kaydet
    df_with_predictions.to_csv('accuracy_test_sonuclari.csv', index=False)
    print("\nTest sonuçları 'accuracy_test_sonuclari.csv' dosyasına kaydedildi.")
    
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

