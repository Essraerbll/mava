import json
import csv

# JSON dosyasını okuyun
with open('TÜM_MARDİN_RESTAURANTLARI.JSON', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# CSV dosyasını oluşturun
with open('Mardin.csv', 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Başlık satırını yazın (JSON'daki anahtarlar)
    header = data[0].keys()  # İlk öğenin anahtarlarını alıyoruz
    csv_writer.writerow(header)

    # Verileri yazın
    for restaurant in data:
        csv_writer.writerow(restaurant.values())

print("JSON dosyası başarıyla CSV'ye dönüştürüldü!")