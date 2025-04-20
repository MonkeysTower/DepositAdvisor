import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def fetch_page(url):
    """
    Подключение к серверу и получение его полного тела.
    """
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--silent")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        hide_button = driver.find_element(By.CSS_SELECTOR, ".Link__sc-pw0az9-0.hHja-Dt")
        driver.execute_script("arguments[0].scrollIntoView(true);", hide_button)
        wait = WebDriverWait(driver, 3)
        driver.execute_script("arguments[0].click();", hide_button)
        wait = WebDriverWait(driver, 3)
        html_content = driver.page_source
        return html_content
    except Exception as e:
        print(e)
        return driver.page_source
    finally:
        driver.quit()

def extract_deposit_info(html_content):
    """
    Извлекает информацию о вкладах из HTML-контента.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    deposits = []
    deposit_containers = soup.find_all("div", class_="resultItemSummarystyled__StyledSummary-sc-1dxdkfw-0 kQexaM")
    for container in deposit_containers:
        name = None
        bank = None
        rate = None
        min_duration = None
        max_duration = None
        min_amount = None
        max_amount = None
        try:
            name_element = container.find("div", class_="Text__sc-vycpdy-0 fZvTEL")
            if name_element:
                name = name_element.text.strip().replace(' (ежемесячно)', '')
            bank_element = container.find("div", class_="Text__sc-vycpdy-0 cIWZzu")
            if bank_element:
                bank = bank_element.text.strip()
            rate_element = container.find("div", class_="Text__sc-vycpdy-0 gwvMGj")
            if rate_element:
                rate = float(rate_element.text.replace('%', '').replace(',', '.').replace('до ', '').strip())
            duration_element = container.find("div", class_="Text__sc-vycpdy-0 grPHnF")
            if duration_element:
                duration = duration_element.text.strip()
                if '—' in duration:
                    min_duration, max_duration = duration.replace(' дн.', '').replace(' ', '').split('—')
                    min_duration = int(min_duration) // 30
                    max_duration = int(max_duration) // 30
                else:
                    min_duration = int(duration.replace(' дн.', '').replace(' ', '')) // 30
                    max_duration = min_duration
            amount_element = container.find_all("div", class_="Text__sc-vycpdy-0 grPHnF")
            if len(amount_element) > 1:
                amount = amount_element[1].text.strip()
                if '—' in amount:
                    if 'млн' in amount:
                        min_amount, max_amount = amount.replace('млн ₽', '').replace(' ', '').split('—')
                        max_amount = float(max_amount) * 1000000
                    else:
                        min_amount, max_amount = amount.replace('₽', '').replace(' ', '').split('—')
                        max_amount = float(max_amount)
                    min_amount = float(min_amount)
                elif 'от' in amount:
                    if 'млн' in amount:
                        min_amount = float(amount.replace('млн ₽', '').replace(' ', '')) * 1000000
                    else:
                        min_amount = float(amount.replace(' ₽', '').replace('от', '').replace(' ', ''))
                elif 'до' in amount:
                    if 'млн' in amount:
                        max_amount = float(amount.replace('млн ₽', '').replace('до', '').replace(' ', '')) * 1000000
                    else:
                        max_amount = float(amount.replace(' ₽', '').replace(' ', ''))
        except Exception as e:
            print(f"Ошибка при извлечении данных из контейнера: {e}")
        deposits.append({
            "Название вклада": name,
            "Название банка": bank,
            "Годовая ставка в %": rate,
            "Минимальный срок": min_duration,
            "Максимальный срок": max_duration,
            "Минимальная сумма": min_amount,
            "Максимальная сумма": max_amount
        })
    return deposits

def start_scraping():
    """
    Запускает процесс парсинга данных о вкладах.
    """
    domain = "https://www.banki.ru/products/deposits/?bank_ids[]=322&banks_ids[]=322&payment_period_per_month=1"
    urls = {
        "all": "",
        "replenishment": "&replenishment=1",
        "withdrawal": "&partial_withdrawal=1",
    }
    urls_data = {}
    for key in urls.keys():
        html_content = fetch_page(domain + urls[key])
        deposits = extract_deposit_info(html_content)
        if deposits:
            urls_data[key] = deposits
        else:
            print(f"Не удалось извлечь данные с {domain + urls[key]}")
    for deposit in urls_data['all']:
        replenishment_opportunity = 'да' if deposit in urls_data["replenishment"] else 'нет'
        withdrawal_opportunity = 'да' if deposit in urls_data["withdrawal"] else 'нет'
        deposit['Возможность пополнения'] = replenishment_opportunity
        deposit['Возможность снятия'] = withdrawal_opportunity
    pd.DataFrame(urls_data['all']).to_csv('./data/deposits.csv', index=False)