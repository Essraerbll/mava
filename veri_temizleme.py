import pandas as pd
import re
import numpy as np

print("=== MARDİN RESTAURANT VERİ TEMİZLEME ===\n")

# CSV dosyasını oku
df = pd.read_csv('Mardin.csv')

print(f"📊 BAŞLANGIÇ:")
print(f"Toplam satır: {len(df):,}")
print(f"Benzersiz restoran: {df['restaurant_name'].nunique()}")

# Rating sütununu çıkar (güvenilir değil)
if 'rating' in df.columns:
    df = df.drop('rating', axis=1)
    print("✅ Rating sütunu çıkarıldı")

# Sadece gerekli sütunları tut
columns_to_keep = ['restaurant_name', 'review_title', 'review_text', 'visit_date', 'travel_type']
df = df[columns_to_keep]

print(f"\n🧹 VERİ TEMİZLEME:")

# 1. Yorum metinlerini birleştir
df['full_review'] = (df['review_title'].fillna("") + " " + df['review_text'].fillna("")).str.strip()

# 2. Emoji ve özel karakterleri temizle
def clean_text(text):
    if pd.isna(text):
        return ""
    
    # Emoji temizleme
    text = re.sub(r'[^\w\sçğıöşüÇĞIÖŞÜ]', ' ', str(text))
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    
    # Başındaki ve sonundaki boşlukları temizle
    text = text.strip()
    
    return text

df['clean_review'] = df['full_review'].apply(clean_text)

# 3. Boş yorumları filtrele
df = df[df['clean_review'].str.len() > 10]  # 10 karakterden uzun yorumlar

# 4. Yorum uzunluğu ekle
df['review_length'] = df['clean_review'].str.len()

print(f"Emoji ve özel karakterler temizlendi")
print(f"Boş yorumlar filtrelendi")
print(f"Yorum uzunluğu hesaplandı")

print(f"\n📈 TEMİZLENMİŞ VERİ:")
print(f"Kalan satır: {len(df):,}")
print(f"Kalan restoran: {df['restaurant_name'].nunique()}")

print(f"\n⭐ YORUM UZUNLUKLARI:")
print(f"En kısa: {df['review_length'].min()} karakter")
print(f"En uzun: {df['review_length'].max()} karakter")
print(f"Ortalama: {df['review_length'].mean():.1f} karakter")

print(f"\n🌍 DİL ANALİZİ:")
# Türkçe karakter tespiti
turkish_chars = ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü', 'Ç', 'Ğ', 'I', 'Ö', 'Ş', 'Ü']
df['has_turkish'] = df['clean_review'].str.contains('|'.join(turkish_chars), na=False)
turkish_count = df['has_turkish'].sum()
print(f"Türkçe karakter içeren: {turkish_count} ({turkish_count/len(df)*100:.1f}%)")

# Örnek temizlenmiş yorumlar
print(f"\n🔍 ÖRNEK TEMİZLENMİŞ YORUMLAR:")
for i in range(min(3, len(df))):
    print(f"\n{i+1}. Restoran: {df.iloc[i]['restaurant_name']}")
    print(f"   Orijinal: {df.iloc[i]['full_review'][:100]}...")
    print(f"   Temizlenmiş: {df.iloc[i]['clean_review'][:100]}...")

# Temizlenmiş veriyi kaydet
output_file = 'Mardin_temiz.csv'
df.to_csv(output_file, index=False)
print(f"\n💾 Temizlenmiş veri kaydedildi: {output_file}")

print(f"\n✅ VERİ TEMİZLEME TAMAMLANDI!")
print(f"Artık sentiment analizi için hazır!")
