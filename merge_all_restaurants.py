#tüm restaurantları tek bir json dosyasında topladık
import json
from pathlib import Path

def merge_all_restaurants():
    """Tüm restaurant review dosyalarını tek bir JSON dosyasında birleştir"""
    print("Tüm Mardin restaurant review dosyalarını birleştiriyorum...")
    
    # Get all JSON files in the current directory that contain "reviews" in the name
    current_dir = Path(".")
    review_files = [f for f in current_dir.glob("*.json") if "reviews" in f.name]
    
    print(f"Bulunan review dosyaları: {len(review_files)}")
    
    # Tüm verileri saklayacak liste
    all_restaurants = []
    
    # Her dosyayı oku ve verileri ekle
    for review_file in review_files:
        try:
            print(f"İşleniyor: {review_file.name}")
            
            with open(review_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Dosya adından restaurant adını çıkar
            restaurant_name = review_file.name.replace('_reviews.json', '')
            
            # Her review'a restaurant_name ekle (eğer yoksa)
            for item in data:
                if isinstance(item, dict):
                    # Restaurant adını ekle
                    if "restaurant_name" not in item:
                        item["restaurant_name"] = restaurant_name
                    
                    # Dosya adını da ekle
                    item["source_file"] = review_file.name
                    
                    all_restaurants.append(item)
            
            print(f"  ✓ {len(data)} review eklendi")
            
        except Exception as e:
            print(f"  ✗ Hata: {e}")
    
    # Birleştirilmiş veriyi kaydet
    output_file = "TÜM_MARDİN_RESTAURANTLARI.JSON"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_restaurants, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Tüm veriler başarıyla birleştirildi!")
        print(f"✓ Çıktı dosyası: {output_file}")
        print(f"✓ Toplam review sayısı: {len(all_restaurants)}")
        print(f"✓ Toplam restaurant dosyası: {len(review_files)}")
        
    except Exception as e:
        print(f"✗ Çıktı dosyası kaydedilirken hata: {e}")

if __name__ == "__main__":
    merge_all_restaurants()
