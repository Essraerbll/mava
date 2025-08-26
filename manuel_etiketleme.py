import pandas as pd
import os
import json
from datetime import datetime

print("=== MARDİN RESTAURANT MANUEL ETİKETLEME ===\n")

# Temizlenmiş veriyi oku
df = pd.read_csv('Mardin_temiz.csv')
total_reviews = len(df)

print(f"📊 TOPLAM: {total_reviews:,} yorum")
print(f"🏪 RESTORAN: {df['restaurant_name'].nunique()} adet")

# Etiketleme kriterleri
print(f"\n📋 ETİKETLEME KRİTERLERİ:")
print(f"N = Negatif (kötü yemek, hizmet, fiyat, temizlik)")
print(f"P = Pozitif (iyi yemek, hizmet, atmosfer, lezzet)")
print(f"O = Nötr (sadece bilgi, kararsız, orta)")
print(f"Q = Çıkış ve kaydet")

# Etiketleme dosyası
etiketleme_file = 'etiketleme_ilerleme.json'

# Mevcut ilerlemeyi yükle
if os.path.exists(etiketleme_file):
    with open(etiketleme_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)
    print(f"\n✅ Mevcut ilerleme yüklendi: {len(progress)} yorum etiketlendi")
else:
    progress = {}
    print(f"\n🆕 Yeni etiketleme başlıyor...")

# Etiketleme fonksiyonu
def etiketle_yorum(index, row):
    print(f"\n{'='*80}")
    print(f"📝 YORUM {index+1}/{total_reviews}")
    print(f"🏪 Restoran: {row['restaurant_name']}")
    print(f"📅 Tarih: {row['visit_date']}")
    print(f"📏 Uzunluk: {row['review_length']} karakter")
    print(f"{'='*80}")
    print(f"📄 YORUM METNİ:")
    print(f"{row['clean_review']}")
    print(f"{'='*80}")
    
    while True:
        choice = input(f"🎯 ETİKET (N/P/O/Q): ").upper().strip()
        
        if choice in ['N', 'P', 'O']:
            return choice
        elif choice == 'Q':
            return 'Q'
        else:
            print(f"❌ Geçersiz seçim! N, P, O veya Q girin.")

# Ana etiketleme döngüsü
print(f"\n🚀 ETİKETLEME BAŞLIYOR...")
print(f"💡 İpucu: Her 50 yorumda bir kayıt yapılır")

batch_size = 50
current_batch = 0

try:
    for i in range(total_reviews):
        # Zaten etiketlenmiş mi kontrol et
        if str(i) in progress:
            continue
            
        row = df.iloc[i]
        etiket = etiketle_yorum(i, row)
        
        if etiket == 'Q':
            print(f"\n💾 Çıkış yapılıyor...")
            break
            
        # Etiketi kaydet
        progress[str(i)] = {
            'etiket': etiket,
            'restaurant': row['restaurant_name'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Her 50 yorumda bir kaydet
        if (i + 1) % batch_size == 0:
            with open(etiketleme_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            print(f"\n💾 {i+1} yorum kaydedildi!")
            print(f"📊 İlerleme: {len(progress)}/{total_reviews} ({len(progress)/total_reviews*100:.1f}%)")
            
            # Mola seçeneği
            mola = input(f"⏸️ Mola mı? (E/H): ").upper().strip()
            if mola == 'E':
                print(f"⏰ Mola verildi. Devam etmek için scripti tekrar çalıştırın.")
                break

except KeyboardInterrupt:
    print(f"\n\n⏹️ Etiketleme durduruldu!")

# Final kayıt
with open(etiketleme_file, 'w', encoding='utf-8') as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)

print(f"\n✅ ETİKETLEME TAMAMLANDI!")
print(f"📊 Toplam etiketlenen: {len(progress)}/{total_reviews}")
print(f"💾 Kayıt dosyası: {etiketleme_file}")

# İstatistikler
if progress:
    etiketler = [p['etiket'] for p in progress.values()]
    print(f"\n📈 ETİKET DAĞILIMI:")
    print(f"Negatif (N): {etiketler.count('N')}")
    print(f"Pozitif (P): {etiketler.count('P')}")
    print(f"Nötr (O): {etiketler.count('O')}")

print(f"\n🎯 Sonraki adım: Etiketlenen verilerle model eğitimi!")
