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

# Buraya kendi çerezlerinizi ekleyin (Application > Cookies kısmından kopyalayın)
manual_cookies = [
    {"name": "OptanonConsent", "value": "isGpcEnabled=1&datestamp=Mon+Jul+14+2025+23%3A33%3A45+GMT%2B0300+(GMT%2B03%3A00)&version=202405.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=8ab1b3af-d818-493b-bfe3-97c9e1a6882a&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.tripadvisor.com%2FSmartDeals-g55252-Only_Tennessee-Hotel-Deals.html%23SPLITVIEWMAP&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0"},
    {"name": "datadome", "value": "qRcOfW2al3Y8FY6GiotEQ4BjXAQwAMfhyx41qLEDZfjP4bvI0pzzxfLvpvkokPofoeXCATU5OoOB2KKotgddsq_jhCr49GrLdcPsTT9VT~~HeCptDCmpPltaQVrr8ehd"},
    {"name": "TASession", "value": "V2ID.B18C25817BDCA31903FD7603B73719DD*SQ.7*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true*EAU._"},
    # ... diğer çerezler ...
]

options = Options()
# options.add_argument('--headless')  # Headless kapalı, insan gibi davran
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=options)

def extract_reviews_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []
    # Önce klasik TripAdvisor reviewCard ile dene
    review_blocks = soup.find_all('div', attrs={'data-automation': 'reviewCard'})
    # Eğer hiç bulamazsa, fallback olarak h1>span içeren div'leri dene
    if not review_blocks:
        for div in soup.find_all('div'):
            h1_tag = div.find('h1')
            if h1_tag and h1_tag.find('span'):
                review_blocks.append(div)
    for review_block in review_blocks:
        try:
            restaurant_name = "Al Hayaal"
            # Kullanıcı adı
            user_name = ""
            h1_tag = review_block.find('h1')
            if h1_tag and h1_tag.find('span'):
                user_name = h1_tag.find('span').text.strip()
            else:
                # Alternatif olarak eski yapı
                user_tag = review_block.find('a', href=True)
                if user_tag and user_tag.text.strip():
                    user_name = user_tag.text.strip()
            # Kullanıcı profil linki
            user_profile_link = ""
            profile_a = review_block.find('a', href=True)
            if profile_a and "/Profile/" in profile_a['href']:
                user_profile_link = base_url + profile_a['href']
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
    # Önce ana sayfaya git ve çerezleri ekle
    driver.get("https://www.tripadvisor.com.tr")
    for cookie in manual_cookies:
        driver.add_cookie(cookie)
    # Sonra asıl sayfaya git
    driver.get(start_url)
    wait = WebDriverWait(driver, 15)
    page_num = 1
    visited_urls = set()
    while True:
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-automation="reviewCard"]')))
            time.sleep(2)  # Ekstra bekleme, yorumlar tam gelsin
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
    with open("all_reviews.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(all_reviews)} yorum kaydedildi.")