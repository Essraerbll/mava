import pandas as pd
import numpy as np

print("=== MARDİN RESTAURANT VERİ ANALİZİ ===\n")

# CSV dosyasını oku
df = pd.read_csv('Mardin.csv')

print(f"📊 GENEL BİLGİLER:")
print(f"Toplam satır: {len(df):,}")
print(f"Benzersiz restoran: {df['restaurant_name'].nunique()}")
print(f"Benzersiz yorum yazan: {df['reviewer_name'].nunique() if 'reviewer_name' in df.columns else 'Bilinmiyor'}")

print(f"\n📋 SÜTUN BİLGİLERİ:")
print(df.info())

print(f"\n🔍 İLK 5 SATIR:")
print(df.head())

print(f"\n📈 RESTORAN BAŞINA YORUM DAĞILIMI:")
restaurant_counts = df['restaurant_name'].value_counts()
print(f"En çok yorum: {restaurant_counts.iloc[0]} ({restaurant_counts.index[0]})")
print(f"En az yorum: {restaurant_counts.iloc[-1]} ({restaurant_counts.index[-1]})")
print(f"Ortalama yorum: {restaurant_counts.mean():.1f}")

print(f"\n⭐ YORUM UZUNLUKLARI:")
if 'review_text' in df.columns:
    df['review_length'] = df['review_text'].str.len()
    print(f"En kısa yorum: {df['review_length'].min()} karakter")
    print(f"En uzun yorum: {df['review_length'].max()} karakter")
    print(f"Ortalama yorum: {df['review_length'].mean():.1f} karakter")

print(f"\n🌍 DİL ANALİZİ:")
if 'review_text' in df.columns:
    # Basit Türkçe karakter tespiti
    turkish_chars = ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü', 'Ç', 'Ğ', 'I', 'Ö', 'Ş', 'Ü']
    df['has_turkish'] = df['review_text'].str.contains('|'.join(turkish_chars), na=False)
    turkish_count = df['has_turkish'].sum()
    print(f"Türkçe karakter içeren yorum: {turkish_count} ({turkish_count/len(df)*100:.1f}%)")

print(f"\n📅 TARİH ANALİZİ:")
if 'review_date' in df.columns:
    df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
    print(f"İlk yorum: {df['review_date'].min()}")
    print(f"Son yorum: {df['review_date'].max()}")
    print(f"Toplam gün: {(df['review_date'].max() - df['review_date'].min()).days}")

print(f"\n💡 ÖNERİLER:")
print("1. Veri temizleme yapılmalı")
print("2. Türkçe yorumlar ayrıştırılmalı")
print("3. Yorum uzunluğu standardize edilmeli")
print("4. Eksik veriler doldurulmalı")
