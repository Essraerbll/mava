import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_prepare_data():
    """Farklı sentiment analizi sonuçlarını yükle ve karşılaştır"""
    
    # Dosyaları yükle
    bert_results = pd.read_csv("restaurant_sentiment_bert_gpu.csv")
    rule_based = pd.read_csv("Mardin_rule_based_sentiment.csv") 
    turkce_sentiment = pd.read_csv("Mardin_turkce_sentiment.csv")
    
    print("BERT Modeli sonuçları:")
    print(f"Toplam restoran: {len(bert_results)}")
    print(f"Ortalama pozitif %: {bert_results['pozitif_%'].mean():.1f}%")
    print(f"Ortalama negatif %: {bert_results['negatif_%'].mean():.1f}%")
    
    print("\nRule-based sonuçları:")
    print(f"Toplam restoran: {len(rule_based)}")
    print(f"Ortalama pozitif %: {rule_based['pozitif_%'].mean():.1f}%")
    print(f"Ortalama negatif %: {rule_based['negatif_%'].mean():.1f}%")
    
    print("\nTürkçe sentiment sonuçları:")
    print(f"Toplam restoran: {len(turkce_sentiment)}")
    print(f"Ortalama pozitif %: {turkce_sentiment['pozitif_%'].mean():.1f}%")
    print(f"Ortalama negatif %: {turkce_sentiment['negatif_%'].mean():.1f}%")
    
    return bert_results, rule_based, turkce_sentiment

def compare_models(bert_results, rule_based, turkce_sentiment):
    """Modelleri karşılaştır ve accuracy hesapla"""
    
    # Ortak restoranları bul
    common_restaurants = set(bert_results['restaurant_name']) & set(rule_based['restaurant_name']) & set(turkce_sentiment['restaurant_name'])
    
    print(f"\nOrtak restoran sayısı: {len(common_restaurants)}")
    
    # Ortak restoranlar için verileri birleştir
    comparison_data = []
    
    for restaurant in common_restaurants:
        bert_row = bert_results[bert_results['restaurant_name'] == restaurant].iloc[0]
        rule_row = rule_based[rule_based['restaurant_name'] == restaurant].iloc[0]
        turkce_row = turkce_sentiment[turkce_sentiment['restaurant_name'] == restaurant].iloc[0]
        
        # Dominant sentiment'i belirle (en yüksek yüzde)
        bert_sentiment = 'pozitif' if bert_row['pozitif_%'] > bert_row['negatif_%'] else 'negatif'
        rule_sentiment = 'pozitif' if rule_row['pozitif_%'] > rule_row['negatif_%'] else 'negatif'
        turkce_sentiment_label = 'pozitif' if turkce_row['pozitif_%'] > turkce_row['negatif_%'] else 'negatif'
        
        comparison_data.append({
            'restaurant_name': restaurant,
            'bert_sentiment': bert_sentiment,
            'rule_sentiment': rule_sentiment,
            'turkce_sentiment': turkce_sentiment_label,
            'bert_pozitif_%': bert_row['pozitif_%'],
            'rule_pozitif_%': rule_row['pozitif_%'],
            'turkce_pozitif_%': turkce_row['pozitif_%']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Accuracy hesapla
    bert_vs_rule = accuracy_score(comparison_df['bert_sentiment'], comparison_df['rule_sentiment'])
    bert_vs_turkce = accuracy_score(comparison_df['bert_sentiment'], comparison_df['turkce_sentiment'])
    rule_vs_turkce = accuracy_score(comparison_df['rule_sentiment'], comparison_df['turkce_sentiment'])
    
    print(f"\n=== ACCURACY SONUÇLARI ===")
    print(f"BERT vs Rule-based: {bert_vs_rule:.3f} ({bert_vs_rule*100:.1f}%)")
    print(f"BERT vs Türkçe: {bert_vs_turkce:.3f} ({bert_vs_turkce*100:.1f}%)")
    print(f"Rule-based vs Türkçe: {rule_vs_turkce:.3f} ({rule_vs_turkce*100:.1f}%)")
    
    # Detaylı karşılaştırma
    print(f"\n=== DETAYLI KARŞILAŞTIRMA ===")
    print("BERT ve Rule-based aynı sonucu veren restoranlar:")
    same_bert_rule = comparison_df[comparison_df['bert_sentiment'] == comparison_df['rule_sentiment']]
    print(f"Sayı: {len(same_bert_rule)}")
    
    print("\nBERT ve Türkçe aynı sonucu veren restoranlar:")
    same_bert_turkce = comparison_df[comparison_df['bert_sentiment'] == comparison_df['turkce_sentiment']]
    print(f"Sayı: {len(same_bert_turkce)}")
    
    # Farklı sonuç veren restoranları göster
    print("\n=== FARKLI SONUÇ VEREN RESTORANLAR ===")
    different_results = comparison_df[comparison_df['bert_sentiment'] != comparison_df['rule_sentiment']]
    
    if len(different_results) > 0:
        print("BERT ve Rule-based farklı sonuç veren restoranlar:")
        for _, row in different_results.head(10).iterrows():
            print(f"- {row['restaurant_name']}: BERT={row['bert_sentiment']}({row['bert_pozitif_%']:.1f}%), Rule={row['rule_sentiment']}({row['rule_pozitif_%']:.1f}%)")
    
    return comparison_df

def create_visualizations(comparison_df):
    """Görselleştirmeler oluştur"""
    
    # 1. Accuracy karşılaştırma grafiği
    models = ['BERT vs Rule', 'BERT vs Türkçe', 'Rule vs Türkçe']
    accuracies = [
        accuracy_score(comparison_df['bert_sentiment'], comparison_df['rule_sentiment']),
        accuracy_score(comparison_df['bert_sentiment'], comparison_df['turkce_sentiment']),
        accuracy_score(comparison_df['rule_sentiment'], comparison_df['turkce_sentiment'])
    ]
    
    plt.figure(figsize=(10, 6))
    plt.bar(models, accuracies, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    plt.title('Model Karşılaştırma - Accuracy Oranları')
    plt.ylabel('Accuracy')
    plt.ylim(0, 1)
    
    for i, v in enumerate(accuracies):
        plt.text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('model_accuracy_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Pozitif yüzde karşılaştırması
    plt.figure(figsize=(12, 8))
    plt.scatter(comparison_df['bert_pozitif_%'], comparison_df['rule_pozitif_%'], 
                alpha=0.6, label='BERT vs Rule-based')
    plt.scatter(comparison_df['bert_pozitif_%'], comparison_df['turkce_pozitif_%'], 
                alpha=0.6, label='BERT vs Türkçe')
    
    plt.plot([0, 100], [0, 100], 'r--', alpha=0.5, label='Mükemmel uyum')
    plt.xlabel('BERT Pozitif %')
    plt.ylabel('Diğer Model Pozitif %')
    plt.title('Pozitif Yüzde Karşılaştırması')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('positive_percentage_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    print("=== MODEL ACCURACY ANALİZİ ===\n")
    
    # Verileri yükle
    bert_results, rule_based, turkce_sentiment = load_and_prepare_data()
    
    # Modelleri karşılaştır
    comparison_df = compare_models(bert_results, rule_based, turkce_sentiment)
    
    # Görselleştirmeler oluştur
    try:
        create_visualizations(comparison_df)
        print("\nGörselleştirmeler 'model_accuracy_comparison.png' ve 'positive_percentage_comparison.png' olarak kaydedildi.")
    except Exception as e:
        print(f"Görselleştirme hatası: {e}")
    
    # Sonuçları CSV olarak kaydet
    comparison_df.to_csv('model_comparison_results.csv', index=False)
    print("\nDetaylı karşılaştırma sonuçları 'model_comparison_results.csv' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
