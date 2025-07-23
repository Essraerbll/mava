import requests
from bs4 import BeautifulSoup
import json
import time

API_KEY = "118f266ebe143b16fef84d16a716b026"

def get_html(url):
    params = {
        'api_key': API_KEY,
        'url': url,
        'render': 'true'
    }
    response = requests.get("http://api.scraperapi.com", params=params)
    return response.text

def get_all_reviews(restaurant_url, restaurant_name):
    all_reviews = []
    page_url = restaurant_url
    while True:
        print(f"{page_url} işleniyor...")
        html = get_html(page_url)
        soup = BeautifulSoup(html, "html.parser")
        review_blocks = soup.find_all('div', attrs={'data-automation': 'reviewCard'})
        for review_block in review_blocks:
            try:
                # Kullanıcı adı ve profil linki
                user_name = ""
                user_profile_link = ""
                # Öncelik: h1 > span[class="OUDwj b u"]
                h1_tag = review_block.find('h1')
                if h1_tag:
                    user_span = h1_tag.find('span', class_='OUDwj b u')
                    if user_span and user_span.text.strip():
                        user_name = user_span.text.strip()
                    elif h1_tag.find('span') and h1_tag.find('span').text.strip():
                        user_name = h1_tag.find('span').text.strip()
                # Fallback: eski yapı (a etiketi)
                if not user_name:
                    user_tag = review_block.find('a', href=True)
                    if user_tag and user_tag.text.strip():
                        user_name = user_tag.text.strip()
                # Profil linki: sadece /Profile/ ile başlayanlar
                profile_a = review_block.find('a', href=True)
                if profile_a and "/Profile/" in profile_a['href']:
                    user_profile_link = "https://www.tripadvisor.com.tr" + profile_a['href']
                # Puan (rating)
                rating = None
                rating_svg = review_block.find('svg', attrs={'data-automation': 'bubbleRatingImage'})
                if rating_svg and rating_svg.find('title'):
                    title_text = rating_svg.find('title').text
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
                    date_lines = date_div.text.split("\n")
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
        # Sonraki sayfa var mı?
        next_link = soup.find('a', attrs={'data-smoke-attr': 'pagination-next-arrow'})
        if next_link and next_link.get('href'):
            page_url = "https://www.tripadvisor.com.tr" + next_link['href']
            time.sleep(2)
        else:
            break
    return all_reviews

if __name__ == "__main__":
    restaurant_url = "https://www.tripadvisor.com.tr/Restaurant_Review-g672951-d20093040-Reviews-Al_Hayaal-Mardin_Mardin_Province.html"
    restaurant_name = "Al Hayaal"
    all_reviews = get_all_reviews(restaurant_url, restaurant_name)
    filename = f"{restaurant_name.replace(' ', '_').lower()}_reviews.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(all_reviews)} yorum kaydedildi.")
