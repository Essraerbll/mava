import json
import csv

# JSON dosyasını oku
with open('TÜM_MARDİN_RESTAURANTLARI_temiz2.JSON', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Eğer data bir liste ise doğrudan yazabiliriz
with open('Mardin.csv', 'w', newline='', encoding='utf-8') as csvfile:
    if isinstance(data, list):
        # Anahtarları başlık olarak al
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    else:
        # Eğer data bir dict ise, uygun şekilde işleyin
        # Örneğin: data = data['restaurants']
        pass