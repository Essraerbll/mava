import json
import os
from selenium_tripadvisor_scrape import scrape_tripadvisor_reviews

# JSON dosyalarının olduğu klasör
JSON_KLASORU = "Restaurants-g672951-Mardin_Mardin_Province"
dosya_listesi = sorted(os.listdir(JSON_KLASORU))

# Tüm JSON dosyalarındaki restoranları oku
tum_restoranlar = []
for dosya in dosya_listesi:
    if dosya.endswith(".json"):
        with open(os.path.join(JSON_KLASORU, dosya), "r", encoding="utf-8") as f:
            veri = json.load(f)
            if isinstance(veri, list):
                tum_restoranlar.extend(veri)

print(f"Toplam restoran sayısı: {len(tum_restoranlar)}")

# Her restoran için yorumları çek
for index, restoran in enumerate(tum_restoranlar, 1):
    isim = restoran.get("name", f"restoran_{index}").replace(" ", "_").replace("/", "_")
    url = restoran.get("url")
    if not url:
        continue

    print(f"{index}{isim} restoranı işleniyor...")
    yorumlar = scrape_tripadvisor_reviews(url)

    with open(f"{index}_{isim}_yorumlar.json", "w", encoding="utf-8") as f:
        json.dump(yorumlar, f, ensure_ascii=False, indent=2)
    print(f"{index}{isim}: {len(yorumlar)} yorum kaydedildi.")
