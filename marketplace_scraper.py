import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

def get_driver():
    """Inicializa o WebDriver do Chrome com configurações otimizadas."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    # Remova o '#' da linha abaixo se quiser que o navegador rode escondido (headless)
    # chrome_options.add_argument("--headless") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def classify_organic(index):
    """Classifica o produto com base na sua posição de exibição (ranking)."""
    if index <= 50:
        return "Muito Orgânico (Alta Demanda)"
    elif index <= 150:
        return "Orgânico (Em Ascensão)"
    else:
        return "Quase Orgânico / Potencial"

def scrape_marketplace(driver, search_query):
    """Realiza o scraping e aplica a lógica de ranking orgânico."""
    search_url = f"https://www.facebook.com/marketplace/search/?query={search_query.replace(' ', '%20')}"
    driver.get(search_url)
    print(f"Acessando busca para: {search_query}...")
    time.sleep(6) 

    # Scroll para carregar os produtos (ajustado para capturar mais itens)
    print("Realizando scroll para mapear volume de mercado...")
    for i in range(5): # Aumente este range para capturar mais que 100-200 itens
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    products = []
    # Seletor principal de itens do Marketplace
    elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")

    print(f"Processando {len(elements)} anúncios encontrados...")

    for index, element in enumerate(elements, start=1):
        try:
            # Seletores atualizados para maior robustez
            name = "Nome não encontrado"
            price = "Preço não encontrado"
            location = "Localização não encontrada"
            
            # Tenta capturar os dados usando seletores de estrutura
            spans = element.find_elements(By.TAG_NAME, "span")
            texts = [s.text.strip() for s in spans if s.text.strip()]
            
            if len(texts) >= 2:
                price = texts[0]
                name = texts[1]
                if len(texts) >= 3:
                    location = texts[2]

            product_link = element.get_attribute('href