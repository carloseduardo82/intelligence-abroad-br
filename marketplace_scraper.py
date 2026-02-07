import time
import re
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

def clean_product_name(name):
    """Limpa o nome do produto para gerar um link de busca mais eficaz."""
    # Remove preços como US$ 100 ou R$ 100,00
    name = re.sub(r'(US\$|R\$)\s*\d+([,\.]\d+)?', '', name)
    
    # Remove termos indesejados (case-insensitive)
    unwanted_terms = ['vende-se', 'urgente', 'vendo']
    for term in unwanted_terms:
        name = re.sub(r'\b' + term + r'\b', '', name, flags=re.IGNORECASE)
        
    return name.strip()

def gerar_link_shopee(nome_produto):
    """Gera um link de busca para o produto na Shopee."""
    return f"https://shopee.com.br/search?keyword={nome_produto.replace(' ', '%20')}"

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
            name = "Nome não encontrado"
            price = "Preço não encontrado"
            location = "Localização não encontrada"
            
            # Tenta capturar os dados usando seletores de estrutura
            spans = element.find_elements(By.TAG_NAME, "span")
            texts = [s.text.strip() for s in spans if s.text.strip()]

            # Nova lógica para extrair os dados
            if texts:
                # O preço geralmente é o primeiro
                price = texts[0]
                
                # O nome é o que vem depois do preço, mas pode haver outros spans
                if len(texts) > 1:
                    # Heurística: O nome do produto geralmente é o texto mais longo
                    # e não contém "R$" ou "US$".
                    possible_names = [t for t in texts[1:] if 'R$' not in t and 'US$' not in t]
                    if possible_names:
                        name = max(possible_names, key=len)

                # A localização geralmente é um dos últimos
                if len(texts) > 2:
                    # Heurística: A localização geralmente contém vírgula ou é um dos últimos itens
                    for t in reversed(texts):
                        if ',' in t or ' ' in t: # Cidades e estados costumam ter espaço
                            location = t
                            break

            # Se o nome ainda for o preço, tenta pegar o próximo texto
            if name == price and len(texts) > 1:
                name = texts[1]
            
            # Limpeza final do nome para não ser igual a localização
            if name == location and len(texts) > 1:
                 # Tenta uma alternativa para o nome
                non_price_loc_texts = [t for t in texts if t != price and t != location]
                if non_price_loc_texts:
                    name = max(non_price_loc_texts, key=len)


            product_link = element.get_attribute('href')
            organic_class = classify_organic(index)
            
            clean_name = clean_product_name(name)
            shopee_link = gerar_link_shopee(clean_name)

            products.append({
                "Ranking Orgânico": organic_class,
                "Nome do Produto": name,
                "Preço": price,
                "Localização": location,
                "Link do Produto": product_link,
                "Oportunidade_Shopee": shopee_link,
                "Analisado em": pd.to_datetime("today").strftime('%Y-%m-%d')
            })
        except Exception as e:
            print(f"Erro ao processar o anúncio {index}: {e}")

    return pd.DataFrame(products)

if __name__ == "__main__":
    import os
    driver = get_driver()
    search_query = "notebook" # Defina seu termo de busca aqui
    df_products = scrape_marketplace(driver, search_query)
    driver.quit()

    if not df_products.empty:
        # Garante que o arquivo seja salvo na mesma pasta do script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = f"relatorio_marketplace_{search_query.replace(' ', '_')}.csv"
        file_path = os.path.join(script_dir, filename)
        
        df_products.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"\nScraping concluído! {len(df_products)} produtos salvos em '{file_path}'.")
    else:
        print("Nenhum produto foi encontrado ou processado.")