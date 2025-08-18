import json
import re

# Dosyayı oku
with open('TÜM_MARDİN_RESTAURANTLARI_temiz.JSON', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Her bir review_text'ten "\nDevamını oku" ve "/Devamını oku" kısmını ve sonrasını sil
for item in data:
    if 'review_text' in item and item['review_text']:
        # Hem \nDevamını oku hem /Devamını oku ve sonrasını siler
        item['review_text'] = re.split(r'(\n|/)devamını oku', item['review_text'], flags=re.IGNORECASE)[0].strip()

# Temizlenmiş veriyi kaydet
with open('TÜM_MARDİN_RESTAURANTLARI_temiz2.JSON', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)