import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Данные из секретов GitHub
TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_screen(clicks, name):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,3000")
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://college.uniyar.ac.ru/расписание-занятий")
    time.sleep(8) # Ждем загрузки PDF-плеера
    
    # Скрываем шапку сайта сразу
    driver.execute_script("""
        var h = document.querySelector('header'); if(h) h.remove();
        var n = document.querySelector('.elementor-location-header'); if(n) n.remove();
    """)

    next_btn = driver.find_element(By.CLASS_NAME, "pdfemb-next")
    for _ in range(clicks):
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(0.3)
    
    time.sleep(4) # Даем прогрузиться таблице
    filename = f"{name}.png"
    driver.find_element(By.CLASS_NAME, "pdfemb-viewer").screenshot(filename)
    driver.quit()
    return filename

# Делаем скриншоты
file21 = get_screen(12, "ИСП-21КО")
file20 = get_screen(11, "ИСП-20")

# Функция отправки и закрепа
def send_and_pin(filepath, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(filepath, 'rb') as img:
        # Отправляем фото
        r = requests.post(url, data={'chat_id': CHAT_ID, 'caption': caption}, files={'photo': img})
        res = r.json()
        
        if res.get('ok'):
            msg_id = res['result']['message_id']
            # Закрепляем отправленное сообщение
            requests.post(f"https://api.telegram.org/bot{TOKEN}/pinChatMessage", 
                          data={'chat_id': CHAT_ID, 'message_id': msg_id, 'disable_notification': True})
            print(f"✅ {caption} отправлено и закреплено.")
        else:
            print(f"❌ Ошибка отправки: {res}")

send_and_pin(file21, "📅 Новое расписание ИСП-21КО")
send_and_pin(file20, "📅 Новое расписание ИСП-20")