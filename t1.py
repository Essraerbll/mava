import requests
from bs4 import BeautifulSoup
import json
import time
import os

API_KEY = "118f266ebe143b16fef84d16a716b026"  # kendi key’in

def get_html(url):
    params = {
        'api_key': API_KEY,
        'url': url,
        'render': 'true'  # JavaScript içeriği render'lamak için
    }
    response = requests.get("http://api.scraperapi.com", params=params)
    return response.text

def load_restaurant_links(json_folder):
    import glob
    restaurant_links = []
    json_files = sorted(glob.glob(os.path.join(json_folder, '*.json')),
                        key=lambda x: int(x.split('_')[-1].replace('.json', '').replace('page', '').replace('-', '').strip()) if 'page' in x else 0)
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'link' in item:
                    restaurant_links.append({
                        'name': item.get('name', ''),
                        'link': item['link']
                    })
    return restaurant_links

if __name__ == "__main__":
    restaurant_url = "https://www.tripadvisor.com.tr/Restaurant_Review-g672951-d20093040-Reviews-Al_Hayaal-Mardin_Mardin_Province.html"
    all_reviews = []
    print(f"{restaurant_url} işleniyor...")
    try:
        html = get_html(restaurant_url)
        with open("debug_al_hayaal.html", "w", encoding="utf-8") as f:
            f.write(html)
        soup = BeautifulSoup(html, "html.parser")
        for review_block in soup.find_all('div', attrs={'data-automation': 'reviewCard'}):
            try:
                restaurant_name = "Al Hayaal"
                # Kullanıcı adı ve profil linki
                user_tag = review_block.find('a', href=True)
                user_name = user_tag.text.strip() if user_tag else ""
                user_profile_link = "https://www.tripadvisor.com.tr" + user_tag['href'] if user_tag else ""
                # Puan (rating)
                rating = None
                rating_svg = review_block.find('svg', attrs={'data-automation': 'bubbleRatingImage'})
                if rating_svg and rating_svg.find('title'):
                    title_text = rating_svg.find('title').text
                    # "5 üzerinden 5 baloncuk üzerinden" gibi bir metin, ilk rakamı al
                    rating = int(title_text.strip()[0])
                # Yorum başlığı
                review_title_tag = review_block.find('div', attrs={'data-test-target': 'review-title'})
                review_title = review_title_tag.text.strip() if review_title_tag else ""
                # Yorum metni
                review_body_tag = review_block.find('div', attrs={'data-test-target': 'review-body'})
                review_text = review_body_tag.text.strip() if review_body_tag else ""
                # Ziyaret tarihi
                visit_date = ""
                date_div = review_block.find('div', class_='fUmAk')
                if date_div:
                    date_lines = date_div.text.split("\\n")
                    for line in date_lines:
                        if "Yazıldığı tarih:" in line:
                            visit_date = line.replace("Yazıldığı tarih:", "").strip()
                # Seyahat tipi
                travel_type = ""
                travel_type_span = review_block.find('span', class_='mcweh')
                if travel_type_span:
                    travel_type = travel_type_span.text.strip()
                all_reviews.append({
                    "restaurant_name": restaurant_name,
                    "user_name": user_name,
                    "user_profile_link": user_profile_link,
                    "rating": rating,
                    "visit_date": visit_date,
                    "travel_type": travel_type,
                    "review_title": review_title,
                    "review_text": review_text
                })
            except Exception as e:
                print(f"Yorum işlenirken hata: {e}")
    except Exception as e:
        print(f"Restoran işlenirken hata: {e}")
    filename = f"{restaurant_name.replace(' ', '_').lower()}_reviews.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(all_reviews)} yorum kaydedildi.")
