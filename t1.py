import requests
from bs4 import BeautifulSoup
import json
import time
import os

API_KEY = "API_KEY_BURAYA_GELECEK"  # Buraya kendi API anahtarınızı girin

def get_html(url):
    encoded_url = requests.utils.quote(url, safe='')
    full_url = f"https://api.webscrapingapi.com/v2?api_key={API_KEY}&url={encoded_url}&render_js=true"
    response = requests.get(full_url)
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
    json_folder = "Restaurants-g672951-Mardin_Mardin_Province"
    all_restaurants = load_restaurant_links(json_folder)
    all_reviews = []
    for idx, restaurant in enumerate(all_restaurants, 1):
        print(f"[{idx}/{len(all_restaurants)}] {restaurant['name']} işleniyor...")
        try:
            html = get_html(restaurant['link'])
            soup = BeautifulSoup(html, "html.parser")
            # Yorumları bulmak için temel bir örnek (TripAdvisor'ın HTML yapısı değişebilir, selector'ları güncellemek gerekebilir)
            for review_block in soup.find_all('div', class_='reviewSelector'):
                try:
                    restaurant_name = restaurant['name']
                    user = review_block.find('div', class_='info_text')
                    user_name = user.text.strip() if user else ""
                    user_profile_link = user.find('a')['href'] if user and user.find('a') else ""
                    rating_tag = review_block.find('span', class_='ui_bubble_rating')
                    rating = int(rating_tag['class'][1].split('_')[-1]) / 10 if rating_tag else None
                    review_title = review_block.find('span', class_='noQuotes').text.strip() if review_block.find('span', class_='noQuotes') else ""
                    review_text = review_block.find('p', class_='partial_entry').text.strip() if review_block.find('p', class_='partial_entry') else ""
                    # Diğer alanlar için ek kodlar eklenebilir
                    all_reviews.append({
                        "restaurant_name": restaurant_name,
                        "user_name": user_name,
                        "user_profile_link": user_profile_link,
                        "rating": rating,
                        "visit_date": "",
                        "travel_type": "",
                        "review_title": review_title,
                        "review_text": review_text,
                        "value_rating": 0,
                        "service_rating": 0,
                        "food_rating": 0,
                        "atmosphere_rating": 0,
                        "helpful_vote_count": 0
                    })
                except Exception as e:
                    print(f"Yorum işlenirken hata: {e}")
            time.sleep(2)  # API'yı yormamak için bekleme
        except Exception as e:
            print(f"Restoran işlenirken hata: {e}")
    with open("all_reviews.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(all_reviews)} yorum kaydedildi.")
