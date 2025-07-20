from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://www.tripadvisor.com.tr"
start_url = base_url + "/Restaurant_Review-g672951-d20093040-Reviews-Al_Hayaal-Mardin_Mardin_Province.html"
all_reviews = []

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=options)

def extract_reviews_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []
    for review_block in soup.find_all('div', attrs={'data-automation': 'reviewCard'}):
        try:
            restaurant_name = "Al Hayaal"
            # Kullanıcı adı ve profil linki
            user_tag = review_block.find('a', href=True)
            user_name = user_tag.text.strip() if user_tag else ""
            user_profile_link = base_url + user_tag['href'] if user_tag else ""
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
            reviews.append({
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
    return reviews

def go_to_next_page():
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[data-smoke-attr="pagination-next-arrow"]')
        next_button.click()
        return True
    except NoSuchElementException:
        return False

if __name__ == "__main__":
    driver.get(start_url)
    wait = WebDriverWait(driver, 15)
    page_num = 1
    visited_urls = set()
    while True:
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-automation=\"reviewCard\"]')))
        except Exception as e:
            print(f"Yorumlar yüklenmedi veya bulunamadı: {e}")
        print(f"Sayfa {page_num} işleniyor: {driver.current_url}")
        html = driver.page_source
        with open(f"debug_page_{page_num}.html", "w", encoding="utf-8") as f:
            f.write(html)
        all_reviews.extend(extract_reviews_from_html(html))
        visited_urls.add(driver.current_url)
        if not go_to_next_page():
            break
        time.sleep(3)
        page_num += 1
        if driver.current_url in visited_urls:
            print("Tekrar eden sayfa tespit edildi, döngü kırılıyor.")
            break
    driver.quit()
    with open("aAl-Hayaal-Restaurant_reviews.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(all_reviews)} yorum kaydedildi.")