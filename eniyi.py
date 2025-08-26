import pandas as pd

# Dosyayı yükle
df = pd.read_csv("restaurant_sentiment_bert_gpu.csv")

# Min yorum filtresi (>=10 yorum)
df_filtered = df[df["toplam"] >= 10].copy()

# Pozitif oranına göre sıralama (yüksekten düşüğe)
top_restaurants = df_filtered.sort_values(
    by=["pozitif_%", "toplam"], ascending=[False, False]
).head(10)

print("=== EN ÇOK POZİTİF ORANA SAHİP RESTORANLAR (min 10 yorum) ===")
print(top_restaurants.to_string(index=False))

print(f"\nToplam {len(df_filtered)} restoran analiz edildi (10+ yorum)")
print(f"En iyi restoran: {top_restaurants.iloc[0]['restaurant_name']} ({top_restaurants.iloc[0]['pozitif_%']}% pozitif)")
