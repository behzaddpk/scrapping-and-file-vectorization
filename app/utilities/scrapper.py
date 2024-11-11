import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def Scrapper(url):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            logging.info(f"Attempting to fetch the URL: {url} (Attempt {attempt + 1}/{retry_attempts})")
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "header, .content-block, article"))
            )

            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            headings = ' '.join([h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])])
            paragraphs = ' '.join([p.text.strip() for p in soup.find_all('p')])
            tables = ' '.join([' '.join([td.text for td in table.find_all('td')]) for table in soup.find_all('table')])
            lists = ' '.join([' '.join([li.text.strip() for li in lst.find_all('li')]) for lst in soup.find_all(['ul', 'ol'])])
            links = ' '.join([a['href'] for a in soup.find_all('a', href=True)])

            content = {
                "Headings": headings,
                "Paragraphs": paragraphs,
                "Tables": tables,
                "Lists": lists,
                "Links": links,
            }

            if not any(content.values()):
                logging.warning("No content found on the page.")
                return "No content found on the page."
            logging.info("Content successfully fetched.")
            return content

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if attempt < retry_attempts - 1:
                logging.info("Retrying...")
                time.sleep(2)
            else:
                logging.error("Failed to fetch the page after several attempts.")
                return "Failed to fetch the page due to a network or rendering error."
        finally:
            driver.quit()