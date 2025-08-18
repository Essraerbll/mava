import re

def temizle_visit_date(text):
    # "visit_date": "18 Haziran 2025\nBu y..." kısmını "visit_date": "18 Haziran 2025" olarak bırakır
    pattern = r'("visit_date":\s*")([^"\n]+)\\nBu y.*?"'
    return re.sub(pattern, r'\1\2"', text)

# Doğru dosya adını kullan!
with open('TÜM_MARDİN_RESTAURANTLARI.JSON', 'r', encoding='utf-8') as f:
    data = f.read()

temizlenmis_data = temizle_visit_date(data)

with open('TÜM_MARDİN_RESTAURANTLARI_temiz.JSON', 'w', encoding='utf-8') as f:
    f.write(temizlenmis_data)