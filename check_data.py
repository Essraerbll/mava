import pandas as pd

# CSV dosyasını oku
df = pd.read_csv('Mardin.csv')

print(f"Toplam satır sayısı: {len(df)}")
print(f"Benzersiz restoran sayısı: {df['restaurant_name'].nunique()}")
print(f"Restoran başına ortalama yorum: {len(df) / df['restaurant_name'].nunique():.1f}")

# En çok yorumu olan restoranlar
print("\nEn çok yorumu olan 10 restoran:")
restaurant_counts = df['restaurant_name'].value_counts().head(10)
for name, count in restaurant_counts.items():
    print(f"{name}: {count} yorum")

# Minimum yorum sayısına göre kaç restoran kalıyor
print(f"\n10+ yorumu olan restoran sayısı: {(df['restaurant_name'].value_counts() >= 10).sum()}")
print(f"5+ yorumu olan restoran sayısı: {(df['restaurant_name'].value_counts() >= 5).sum()}")
print(f"1+ yorumu olan restoran sayısı: {(df['restaurant_name'].value_counts() >= 1).sum()}")
