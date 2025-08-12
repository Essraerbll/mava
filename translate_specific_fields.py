#yazılımın çalışması için türkçe karakterleri kaldırdık
import json
import re
from pathlib import Path

def detect_language(text):
    """Detect if text contains non-Turkish characters"""
    # Türkçe karakterler
    turkish_chars = set('çğıöşüÇĞIÖŞÜ')
    
    text_chars = set(text)
    
    # Eğer sadece İngilizce karakterler varsa ve Türkçe karakter yoksa
    if not text_chars.intersection(turkish_chars) and len(text.split()) > 0:
        # Basit bir kontrol - eğer Türkçe kelimeler yoksa İngilizce olabilir
        turkish_words = ['bir', 've', 'bu', 'ile', 'için', 'gibi', 'kadar', 'sonra', 'önce', 'yok', 'var', 'çok', 'güzel', 'iyi', 'kötü']
        has_turkish_word = any(word in text.lower() for word in turkish_words)
        if not has_turkish_word:
            return 'english'
    
    return 'turkish'

def translate_text(text, source_lang):
    """Translate text to Turkish based on detected language"""
    translations = {
        'english': {
            'friends': 'arkadaşlar',
            'family': 'aile',
            'couples': 'çiftler',
            'business': 'iş',
            'solo': 'tek başına',
            'none': 'belirtilmemiş',
            'very good': 'çok iyi',
            'excellent': 'mükemmel',
            'delicious': 'lezzetli',
            'amazing': 'harika',
            'wonderful': 'harika',
            'terrible': 'berbat',
            'bad': 'kötü',
            'good': 'iyi',
            'nice': 'güzel',
            'beautiful': 'güzel',
            'fantastic': 'fantastik',
            'great': 'harika',
            'perfect': 'mükemmel',
            'awesome': 'harika',
            'superb': 'mükemmel',
            'outstanding': 'olağanüstü',
            'brilliant': 'harika',
            'fabulous': 'muhteşem',
            'marvelous': 'harika',
            'splendid': 'muhteşem',
            'gorgeous': 'muhteşem',
            'amazing food': 'harika yemek',
            'great service': 'harika servis',
            'good food': 'iyi yemek',
            'bad service': 'kötü servis',
            'terrible food': 'berbat yemek',
            'excellent service': 'mükemmel servis',
            'wonderful experience': 'harika deneyim',
            'fantastic atmosphere': 'fantastik atmosfer',
            'beautiful place': 'güzel yer',
            'nice staff': 'güzel personel',
            'perfect meal': 'mükemmel yemek',
            'awesome taste': 'harika tat',
            'superb quality': 'mükemmel kalite',
            'outstanding food': 'olağanüstü yemek',
            'brilliant chef': 'harika şef',
            'fabulous restaurant': 'muhteşem restoran',
            'marvelous cuisine': 'harika mutfak',
            'splendid meal': 'muhteşem yemek',
            'gorgeous view': 'muhteşem manzara'
        }
    }
    
    if source_lang in translations:
        translated_text = text
        for original, translation in translations[source_lang].items():
            translated_text = translated_text.replace(original, translation)
            translated_text = translated_text.replace(original.capitalize(), translation.capitalize())
            translated_text = translated_text.replace(original.upper(), translation.upper())
        return translated_text
    
    return text

def process_json_file(file_path):
    """Process a JSON file and translate specific fields"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        translations_made = []
        
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    # Sadece belirtilen alanları kontrol et
                    if key in ['travel_type', 'review_title', 'review_text'] and isinstance(value, str) and value.strip():
                        detected_lang = detect_language(value)
                        if detected_lang != 'turkish':
                            original_text = value
                            translated_text = translate_text(value, detected_lang)
                            
                            if original_text != translated_text:
                                item[key] = translated_text
                                modified = True
                                translations_made.append({
                                    'field': key,
                                    'original': original_text,
                                    'translated': translated_text,
                                    'language': detected_lang
                                })
        
        if modified:
            # Save the modified file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Updated {file_path}")
            print(f"  Translations made:")
            for trans in translations_made:
                print(f"    {trans['field']}: '{trans['original']}' -> '{trans['translated']}' ({trans['language']})")
        else:
            print(f"- No changes needed for {file_path}")
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")

def main():
    print("JSON dosyalarında travel_type, review_title ve review_text alanlarını Türkçeye çeviriyorum...")
    
    # Get all JSON files in the current directory that contain "reviews" in the name
    current_dir = Path(".")
    review_files = [f for f in current_dir.glob("*.json") if "reviews" in f.name]
    
    print(f"Bulunan review dosyaları: {len(review_files)}")
    
    for review_file in review_files:
        print(f"\nİşleniyor: {review_file.name}")
        process_json_file(review_file)
    
    print("\nÇeviri işlemi tamamlandı!")

if __name__ == "__main__":
    main()
