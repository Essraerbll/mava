#selenium ile yapılan çalışma
# tüm restaurantların bilgilerini çekmeye ayarlanmıştı 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
import os
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://www.tripadvisor.com.tr"

# Buraya kendi çerezlerinizi ekleyin (Application > Cookies kısmından kopyalayın)
manual_cookies = [
    {"name": "__Host-3PLSID", "value": "o.calendar.google.com|o.chromewebstore.google.com|o.console.cloud.google.com|o.console.firebase.google.com|o.drive.google.com|o.gds.google.com|o.groups.google.com|o.lens.google.com|o.mail.google.com|o.myaccount.google.com|o.photos.fife.usercontent.google.com|o.photos.google.com|o.play.google.com|o.takeout.google.com|s.TR|s.youtube:g.a000yAjvPvSPOlVSrgXdR4QZV67hz05O3aAiGqn3fLIeEsZkFBeMaHByyeSA4OzuTh-1mmXN1wACgYKAWcSARISFQHGX2MiG-r-MvnAv6voGcxZx83EzBoVAUF8yKp3kJyK-mdcegfEp-VhX8Ub0076"},
    {"name": "_Host-GAPS", "value": "1:wbnxrwjtVSQjdjLOgfjxRoMO41otRHtqRMaHbzEMRO-JH4EZyiZdvzebmkcCFYXFvCCjZ9JuO8azKB98FBeqowY1izv58w:UXh865mtqmBDF3_"},
    {"name": "__Secure-1PAPISID", "value": "gdZautOl9whDBJig/AVDI88q4stdFm8Hhm"},
    {"name": "__Secure-1PSID", "value": "g.a000zAjvPkfJgn9qLnJDswkMFozLYIR5ga0o-7tIhbnpa8ZKOaFH_Zd0pJNhVlq4ifEPKO7gbgACgYKAYkSARISFQHGX2MiYt_PTVmrT23wlAoUVddETBoVAUF8yKoTgglgDkGLXHV7CrX_nHM80076"},
    {"name": "__Secure-1PSIDCC", "value": "AKEyXzXjqvoKb5SXGAQJZghyUyCdtR2FIBsU6IW7oXEKsWPibpLxk2DcXgHjrgY3SAbWC1Ly2qk"},
    {"name": "__Secure-1PSIDTS", "value": "sidts-CjIB5H03P4rSCgjLIN7-vWh90nUzdxbp43DWXsGTYMFIlPnLei3Jnyr0aYVQdf61399FlhAA"},
    {"name": "__Secure-3PAPISID", "value": "gdZautOl9whDBJig/AVDI88q4stdFm8Hhm"},
    {"name": "__Secure-3PSID", "value": "g.a000zAjvPkfJgn9qLnJDswkMFozLYIR5ga0o-7tIhbnpa8ZKOaFHLBtAo9Is_9T11qQNMKlAOQACgYKAYESARISFQHGX2MifqYmwTJym1fdXw74MvXYuxoVAUF8yKptX83AMvGcU7IRTR1lWOIS0076"},
    {"name": "__Secure-3PSIDCC", "value": "AKEyXzUtZiD3ow344IiMPb1vLiBg8QB57stKa9Q_dUuNaWqc9s4-iYKBtRb5Jb9l7U2e1N9291o"},
    {"name": "__Secure-3PSIDTS", "value": "sidts-CjIB5H03P4rSCgjLIN7-vWh90nUzdxbp43DWXsGTYMFIlPnLei3Jnyr0aYVQdf61399FlhAA"},
    {"name": "__Secure-ENID", "value": "28.SE=Lr2xruziF5gAUKsppwYxjmwjSiSpeIQ8ywmLtLNx4R72YTwd3CywPlQfL-oZkz7jGBRgHCGs9X0VVhw81i4lAOevpB_Yjbh5ZOtbkGXYw_ITyXHEn_XWU6dAlT5iosQjsR_D5qSQr5nP4UId33HwEQQP1-3_fyAvzReA9glBwiZGJmqywzvc_4yk0v6zn1fwQU8-3niV7HxaWU1gtcGO0xjoVi7CPn4aQ63boJn9I1anKVYEDLPlrqhuj7MTXozKFZyusx_lu7tk8HOdgx9gKtEn9BFmvWCn-G5O6GBzFa3kGIp0lR-4Omc"},
    {"name": "ACCOUNT_CHOOSER", "value": "AFx_qI7erJ6PVTB236wgrsnVzzEnK9gBCJfYP5x1tDQWzGM0AkZdVWicsAxGRuVacM-8y1lvPCyuVq6TCy3J1s8K0iXRmZj0POkaVc4hgAXGN7E3ClHNdPr39QfR35QX2TbEcW7R93Uge1BqLRKg-t39KE6IVb6lkMxRCbMhHujg6CoEDwef5Z_VASMiJKmDw48rutephxvV5OAW3wIb58ik5gEYN9GK2YaOClWpIxGJmSO_x78Lqq7t-8abAts2VG41iCmJll_7iAmw9xYVGTtxcOSeHnVtIx9Iibda2QKTNOFsDLr2MJ8_HNd_C2Jhedl7Z15ynQPBdG63QLQlKkqumTLX-SgJo-VaMpPzDzCgkoODWHcbtgU"},
    {"name": "AEC", "value": "AVh_V2g7yROnMwZzd46JVTQLpfwpFgfEGIsE_TRnL5E0b8iOS_ZJURJl5hU"},
    {"name": "APISID", "value": "nan"},
    {"name": "datadome", "value": "Gl4c7N5JeRv2PtsD2~qJe0xnYgnv7cRkfSUG41LlIYagZYlgVZZiMlXUj9YVQ5wP9mg4yl7nvsfuJ3VFBa1EHEmfeIUSafrs3~iSqMWUbGsqfYf1m8ZNPBBQrDTZSgSZ"},
    {"name": "datadome", "value": "Y~aaTnWkdHpDTjiYxT0mfV~6k_KpyJ7pdBBQPwvVUckZl0VWvZsvPK~9QXAssbd58NnwiR1GLB9BWekkHusHreYc2AWr8zMdrh80lUXrCaVr9_LsRkaS7CPxgzOK~K3w"},
    {"name": "HSID", "value": "AGlmrvbpABwAXjxEX"},
    {"name": "LSID", "value": "o.calendar.google.com|o.chromewebstore.google.com|o.console.cloud.google.com|o.console.firebase.google.com|o.drive.google.com|o.gds.google.com|o.groups.google.com|o.lens.google.com|o.mail.google.com|o.myaccount.google.com|o.photos.fife.usercontent.google.com|o.photos.google.com|o.play.google.com|o.takeout.google.com|s.TR|s.youtube:g.a000yAjvPvSPOlVSrgXdR4QZV67hz05O3aAiGqn3fLIeEsZkFBeMn0v0oq2WyCLSQuHEXBRlCAACgYKAXkSARISFQHGX2Mivv9dM7IMxGec0tTzVJuK-RoVAUF8yKqFs7lARzEDYNRuZV4-49Ij0076"},
    {"name": "LSOLH", "value": "SVI_ELjkt8um_40DGAkiP01BRURIZl9xbWg0RUp2VG5MMFhDMVg4VnB4MlVrV2piTWw3UDBNUTlGcVhwRGE5ZUcyQnNfM0IxZnZJcmFWSQ:29173323:4fb1"},
    {"name": "NID", "value": "525=LyRAGm7i-vwoyo9-ex3FGP4nekygYjRky4Ma63xQ6ZZPRShxipOeE82Q2lORuP0PFEzc5VpkKfwPDVupJ4z4UoVt1Ods4MHpgyfATC2TOjvdCUlMdKSUjsMI73C7MnoOawEVgnAVP2c6XHmyy4Ho64pMUczwY6ZQbOq9ZDwp50vVviJltk9EsPE22rAC1b-9PM4Z8WEnfB7bzK21QX3S0Qiaw7oVJkUarQ-7lOBe6JJ5AHkPDGy3LzdqKjYO-2XPvWAHlNeufm71u9wTQxG8YMNFSgX7eDV438aVHcQB7YNC9MzIBr9JrtuOpbMbA-XePd_VHkpmpLKyDKtkutg7WaO6zOm9QV75jJGOSDgUIf_kjbeyNGiOOc6s5X-KQBncD980GTIHI8AEDLP43QdCDRQCPh7XSiZDbUkUmjUo5nCWGiwZJU7kdq23H2PzpDIptDgQydcGRIrR28EzzyuwLrVJxF_zEnbIMQd86rV9rdyMMAfy2bJaHUytdGaur2RZv-yeXucoPUybaz54p5Ry8Z5Z1NtK6fN2HDoxDT81plCPmJcc_eOLXgNHDZbFN4fCusXlCqY2KhYcnrZZ_f3xL1_KpbeYyZB9Wbw7keZfUh6BYC2oiBN70psRbHwi-Lg-7y255cO5RkLw_sJRU4pJjFwL5u6Tx01JGwSE7dYUu_XP7TK9t3chfSFonaAdlvZev6I3FxPU0F2-d22HV-mHeLnrqD5NELb_vMB2mz-lZkgDhrDqM7IzUeGKLPxCetnaBYxTF2TOnX8fHFEUa4PuHH3LoD4_KcAER-AIKqsO-o46P6068X8SkUUMDy-496t2dREzIaBD57ypKUsI-6kre2lbfPHzOcRpu6uq7GyDj1q3dA-5ZFA3TItAf5CxXpltxyNX24_e23TJ-wKdMXx6qSFfTdY90TI-5FLkxMed68UBcsJphPOFU1c5SqD0HTq3vGLpeeWF9JX9dWF8hO_ZCp_R5QQ-DEf_X5njagLi90KUeii9_v7Krf5F9jfy2tWTqha3E5EqYg0gKwLrVNhqoKHV4oGlUBFJRGCSIjzpzZYYQXLEzaDPYnTSxsMXjS1kGxU1laqo-jTaVntmuQoK9TNb9TceYfJ-pMFW8xpMFTjSdYlAQO2BN3G1w_lhez4-f2A-VnVolypBk8_6NG7lsYo_JtoIa6jSkm8cUHHJxE27ACod5tdXP5CfhZUrtL7qoO1QtClM893Dbxn979Ee9s3Yzb9xximSx6Rjbu-uqJm5serF_6GVI9IntrmHYImGqwy4LvMepKqOSza9a2xNVCVEbc4TuDM8fT1LjPNTtL6LklQjbdqRIpWi--yfDzK-rFaySR9wCWtRQydsc-jlRyt6meVQC6_jyFcWWh42bB0QK_eoRfN7kkEd0cE_W_3VATl7Th57v7U2PwuQz0n0JC6NtKj05qS3MNdIdcClKiQh4O3KXMebdK6LsIalocshrvCDxB6FRgWYjUZgBQ73pxMlOUdYCO5wCxE6FfkJnhaO_X6jjEr-jakjOs3DfppnbaaTKZwb6TKn2zct"},
    {"name": "OptanonConsent", "value": "isGpcEnabled=1&datestamp=Sat+Jul+19+2025+17%3A52%3A56+GMT%2B0300+(GMT%2B03%3A00)&version=202405.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=d881e226-d1e1-4a06-ba10-c6795e674414&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0&AwaitingReconsent=false"},
    {"name": "OptanonConsent", "value": "isGpcEnabled=1&datestamp=Mon+Jul+14+2025+23%3A33%3A45+GMT%2B0300+(GMT%2B03%3A00)&version=202405.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=8ab1b3af-d818-493b-bfe3-97c9e1a6882a&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.tripadvisor.com%2FSmartDeals-g55252-Only_Tennessee-Hotel-Deals.html%23SPLITVIEWMAP&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A0"},
    {"name": "PAC", "value": "ABlRi839M1rIWI9AVGVNMVGoDekXdbO8l-2REqXNlAUv9MVGGPkkmil0cHYVZtjlTH7Rq5yvblrzzk7nu1IDyGUmkNLrTvJAV_msogcGoeMAiriST_dN5rUwjeuUVH5aIdRc86DLTE3D3ta15RYzEaWsmu7TFZuqGrP9WO17ZakQXk85Kj9aG9OX2ubNCPYEAJjGoxmV8clV5AHfuhoaJiNb0YCmE7Odvm4UCHsbbrc7"},
    {"name": "PMC", "value": "V2*MS.92*MD.20250714*LD.20250717"},
    {"name": "SAPISID", "value": "gdZautOl9whDBJig/AVDI88q4stdFm8Hhm"},
    {"name": "SEARCH_SAMESITE", "value": "CgQItZ4B"},
    {"name": "SID", "value": "g.a000zAjvPkfJgn9qLnJDswkMFozLYIR5ga0o-7tIhbnpa8ZKOaFHkUVCbxzyAWEISNwF-74KrQACgYKAZwSARISFQHGX2MiVg4VGS6rh46-ymULl4g1MxoVAUF8yKpyykXc2-GfJnPuZv1vVRbr0076"},
    {"name": "SIDCC", "value": "AKEyXzUnmV4mCMANLg16TGRU0PKVzQ0iJawdZnzX71_wGRruaQdHSkBN2FJOVop0zPauXsTywfGR"},
    {"name": "SMSV", "value": "ADHTe-Bxyd0u7bTkQMizqosRJL3R_zcRrHn8XP8uPH2dP2oNchvbm9OzaT0Z50GG5AdnEcfn9ApnZd8_K_C5f2fbft5WJdYGbw"},
    {"name": "SSID", "value": "AjgnVhF0khhi3Vstd"},
    {"name": "TADCID", "value": "5mNEmdn8MaJDneibABQCJ4S5rDsRRMescG99HippfocFSR9BVe8oQOW3NKFhjqZBK72KG7LhevNF6xgWzDqlwcpmIqDh6fgsX3c"},
    {"name": "TASameSite", "value": "1"},
    {"name": "TASession", "value": "V2ID.025C6645AF275756EA098605A26335D1*SQ.1*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true"},
    {"name": "TASSK", "value": "enc%3AANY0NPv13BwhnH%2B8%2BPe49QZlbljk4Y9WVPVG8VSrvbmrcmbpGrPNgkxQemkcBvwy9ArfiTXNoTNmNXLT9g6yr9xrFwtn4DiPkwFWDeIzpULc2MEu8TzPaF9Dui2T7w2ggQ%3D%3D"},
    {"name": "TATravelInfo", "value": "V2*A.2*MG.-1*HP.2*FL.3*RS.1"},
    {"name": "TATrkConsent", "value": "eyJvdXQiOiJBRFYsU09DSUFMX01FRElBIiwiaW4iOiJBTkEsRlVOQ1RJT05BTCJ9"},
    {"name": "TAUD", "value": "LA-1752513129195-1*RDD-1-2025_07_14*LG-257141903-2.1.F.*LD-257141904-....."},
    {"name": "TAUnique", "value": "%1%enc%3APigUWlEoojtC3xxw7Sx81ckm13qbvbpheXFs5oT1BqanaSbcfnOL6%2FgiCQMyvuf4Nox8JbUSTxk%3D"},
    {"name": "TAUnique", "value": "%1%enc%3A%2BJAR0F0tPFRorohB9j2tdCPSCwxeP38j8wK2pHzcyQ4lOEF3njpQGoOLcoDepwlRNox8JbUSTxk%3D"}
]

def clean_restaurant_name(name):
    """Restaurant adını temizler ve klasör adı için uygun hale getirir"""
    # Sayı ve nokta ile başlayan kısmı kaldır (örn: "1.Al Hayaal" -> "Al Hayaal")
    name = re.sub(r'^\d+\.\s*', '', name)
    # Özel karakterleri temizle
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Çoklu boşlukları tek boşluğa çevir
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def extract_reviews_from_selenium(driver, restaurant_name):
    """t3.py'den kopyalanan mükemmel yorum çekme fonksiyonu"""
    reviews = []
    review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-automation="reviewCard"]')
    print(f"Bulunan yorum kartı sayısı: {len(review_elements)}")

    for elem in review_elements:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            time.sleep(0.5)

            # 🔽 Devamını oku butonuna tıkla (varsa)
            try:
                more_button = elem.find_element(By.CSS_SELECTOR, 'span[data-test-target="expand-review"]')
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(0.5)
            except:
                pass  # buton yoksa devam

            # Profil linki
            user_profile_link = ""
            try:
                links = elem.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/Profile/" in href:
                        user_profile_link = href
                        break
            except:
                pass

            # Kullanıcı adı - önce profil linkinden çıkar, bulamazsa sayfadan al
            user_name = "Anonim"
            
            # Profil linkinden kullanıcı adını çıkar
            if user_profile_link:
                match = re.search(r'/Profile/([^/?]+)', user_profile_link)
                if match:
                    username_from_link = match.group(1)
                    # Eğer kullanıcı adı geçerliyse kullan
                    if username_from_link and not username_from_link.isdigit() and len(username_from_link) >= 2:
                        user_name = username_from_link
            
            # Eğer profil linkinden çıkarılamadıysa sayfadan al
            if user_name == "Anonim":
                try:
                    user_name = elem.find_element(By.CSS_SELECTOR, 'span.OUDwj.b.u').text.strip()
                except:
                    try:
                        user_name = elem.find_element(By.CSS_SELECTOR, 'h1 span').text.strip()
                    except:
                        pass

            # Puan
            rating = None
            try:
                svg_elem = elem.find_element(By.CSS_SELECTOR, 'svg[data-automation="bubbleRatingImage"]')
                title = svg_elem.find_element(By.TAG_NAME, "title").get_attribute("textContent")
                rating = int(title.strip()[0])
            except:
                pass

            # Yorum başlığı
            review_title = ""
            try:
                review_title = elem.find_element(By.CSS_SELECTOR, 'div[data-test-target="review-title"]').text.strip()
            except:
                pass

            #  Yorum metni
            review_text = ""
            try:
                # Önce daha fazlasını göster'e tıkla (varsa)
                try:
                    more_button = elem.find_element(By.CSS_SELECTOR, 'span[data-test-target="expand-review"]')
                    driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(0.5)
                except:
                    pass

                # Tüm içeriği al
                review_body = elem.find_element(By.CSS_SELECTOR, 'div[data-test-target="review-body"]')
                review_text = review_body.text.strip()

            except Exception as e:
                print(f"Yorum metni alınamadı: {e}")
                review_text = ""

            # Ziyaret tarihi
            visit_date = ""
            try:
                date_div = elem.find_element(By.CSS_SELECTOR, 'div.fUmAk')
                if "Yazıldığı tarih:" in date_div.text:
                    visit_date = date_div.text.replace("Yazıldığı tarih:", "").strip()
            except:
                pass

            # Seyahat tipi
            travel_type = ""
            try:
                travel_type = elem.find_element(By.CSS_SELECTOR, 'span.mcweh').text.strip()
            except:
                pass

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

def go_to_next_page(driver):
    """Sonraki sayfaya geçer - t3.py'den kopyalandı"""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[data-smoke-attr="pagination-next-arrow"]')
        next_button.click()
        return True
    except NoSuchElementException:
        return False

def scrape_restaurant_reviews(restaurant_name, restaurant_link, driver):
    """Tek bir restaurant için yorumları çeker - t3.py'deki algoritma"""
    print(f"\n{'='*50}")
    print(f"Restaurant: {restaurant_name}")
    print(f"Link: {restaurant_link}")
    print(f"{'='*50}")
    
    all_reviews = []
    
    try:
        # Restaurant sayfasına git
        driver.get(restaurant_link)
        time.sleep(15)  # Daha uzun bekleme süresi
        wait = WebDriverWait(driver, 30)  # Daha uzun timeout
        
        page_num = 1
        visited_urls = set()
        
        while True:
            try:
                print(f"Sayfa yükleniyor: {driver.current_url}")
                
                # Sayfanın tam yüklenmesini bekle
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div[data-test-target="review-title"]')
                    )
                )
                time.sleep(5)  # Ek bekleme
                
                print(f"Sayfa {page_num} işleniyor: {driver.current_url}")
                
                # Yorumları çıkar
                page_reviews = extract_reviews_from_selenium(driver, restaurant_name)
                print(f"Bu sayfada {len(page_reviews)} yorum bulundu")
                all_reviews.extend(page_reviews)
                
                visited_urls.add(driver.current_url)
                
                if not go_to_next_page(driver):
                    print("Sonraki sayfa bulunamadı, döngü sonlandırılıyor")
                    break
                    
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                page_num += 1
                
                if driver.current_url in visited_urls:
                    print("Tekrar eden sayfa tespit edildi, döngü kırılıyor.")
                    break
                    
            except Exception as e:
                print(f"Sayfa işlenirken hata: {e}")
                break
        
        return all_reviews
        
    except Exception as e:
        print(f"Restaurant işlenirken hata: {e}")
        return []

def main():
    """Ana fonksiyon"""
    # Restaurant JSON dosyalarının bulunduğu klasör
    restaurants_folder = "Restaurants-g672951-Mardin_Mardin_Province"
    
    # Driver'ı kur
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Ana sayfaya git ve çerezleri ekle
        driver.get("https://www.tripadvisor.com.tr")
        time.sleep(5)  # Sayfanın tam yüklenmesini bekle
        for cookie in manual_cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Çerez eklenemedi: {cookie['name']} - {e}")
        
        # Tüm JSON dosyalarını oku
        json_files = [f for f in os.listdir(restaurants_folder) if f.endswith('.json')]
        json_files.sort()  # Sıralı işlem için
        
        total_restaurants = 0
        processed_restaurants = 0
        
        for json_file in json_files:
            print(f"\n{'#'*60}")
            print(f"JSON dosyası işleniyor: {json_file}")
            print(f"{'#'*60}")
            
            with open(os.path.join(restaurants_folder, json_file), 'r', encoding='utf-8') as f:
                restaurants = json.load(f)
            
            total_restaurants += len(restaurants)
            
            for restaurant in restaurants:
                restaurant_name = restaurant.get('name', '')
                restaurant_link = restaurant.get('link', '')
                
                if not restaurant_link:
                    print(f"Link bulunamadı: {restaurant_name}")
                    continue
                
                # Restaurant adını temizle
                clean_name = clean_restaurant_name(restaurant_name)
                
                # Eğer zaten yorum dosyası varsa atla
                reviews_file = f"{clean_name}_reviews.json"
                if os.path.exists(reviews_file):
                    print(f"Zaten mevcut: {clean_name}")
                    processed_restaurants += 1
                    continue
                
                # Yorumları çek
                reviews = scrape_restaurant_reviews(clean_name, restaurant_link, driver)
                
                if reviews:
                    # Yorumları kaydet
                    with open(reviews_file, 'w', encoding='utf-8') as f:
                        json.dump(reviews, f, ensure_ascii=False, indent=2)
                    print(f"✅ {len(reviews)} yorum kaydedildi: {clean_name}")
                else:
                    print(f"❌ Yorum bulunamadı: {clean_name}")
                
                processed_restaurants += 1
                print(f"İlerleme: {processed_restaurants}/{total_restaurants}")
                
                # Her restaurant arasında kısa bekleme
                time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"İşlem tamamlandı!")
        print(f"Toplam restaurant: {total_restaurants}")
        print(f"İşlenen restaurant: {processed_restaurants}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Ana işlemde hata: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()