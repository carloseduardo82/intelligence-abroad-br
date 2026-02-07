import time
import re
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException

# --- CONFIGURAÇÕES DO MOTOR ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def clean_product_name(name):
    name = re.sub(r'(US\$|R\$)\s*\d+([,\.]\d+)?', '', name)
    unwanted_terms = ['vende-se', 'urgente', 'vendo', 'novo', 'usado']
    for term in unwanted_terms:
        name = re.sub(r'\b' + term + r'\b', '', name, flags=re.IGNORECASE)
    return name.strip()

def scrape_segment(driver, query):
    search_url = f"https://www.facebook.com/marketplace/search/?query={query.replace(' ', '%20')}"
    driver.get(search_url)
    print(f"🔍 Escaneando Segmento: {query.upper()}...")
    time.sleep(5) 

    # Scroll para capturar volume
    for _ in range(3): 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    data = []
    elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")
    
    for index, el in enumerate(elements[:100], start=1): # Limitado a 100 por categoria para velocidade
        try:
            spans = el.find_elements(By.TAG_NAME, "span")
            texts = [s.text.strip() for s in spans if s.text.strip()]
            
            if len(texts) < 2: continue
            
            preco = texts[0]
            nome = max([t for t in texts[1:] if 'R$' not in t], key=len)
            
            # Peso para ordenação decrescente (mais orgânico = maior peso)
            peso = 1000 - index 
            
            data.append({
                "Prioridade": peso,
                "Segmento": query.capitalize(),
                "Produto": nome,
                "Preço": preco,
                "Link": el.get_attribute('href'),
                "Shopee": f"https://shopee.com.br/search?keyword={clean_product_name(nome).replace(' ', '%20')}"
            })
        except: continue
    return pd.DataFrame(data)

# --- EXECUÇÃO GLOBAL ---
if __name__ == "__main__":
    import os
    
    # 1. LISTA DE SEGMENTOS (O CORAÇÃO DA SUA VARREDURA)
    # Adicione ou remova categorias aqui conforme sua estratégia
    meus_segmentos = [
        # ELETRÔNICOS (Alta Margem)
        "iPhone 13", "Notebook Dell", "Cadeira Gamer", "Playstation 5", "Monitor 4K",
        # BELEZA & COSMÉTICOS (Alta Recorrência)
        "Perfume Árabe", "Skincare", "Escova Secadora", "Maquiagem",
        # CASA & UTILIDADES (Alta Demanda Local)
        "Air Fryer", "Robô Aspirador", "Cafeteira Nespresso", "Móveis Madeira",
        # FITNESS & SAÚDE
        "Creatina", "Whey Protein", "Smartwatch Amoled", "Kit Halteres"
    ]

    driver = get_driver()
    lista_consolidada = []

    print(f"🚀 INICIANDO VARREDURA GLOBAL EM {len(meus_segmentos)} SEGMENTOS...")

    for segmento in meus_segmentos:
        try:
            # Roda o scraper para cada item da lista
            df_categoria = scrape_segment(driver, segmento)
            
            if not df_categoria.empty:
                # Adiciona uma coluna para você saber de qual segmento veio o produto
                df_categoria['Segmento_Original'] = segmento.capitalize()
                lista_consolidada.append(df_categoria)
                print(f"✅ {len(df_categoria)} produtos capturados em: {segmento}")
            
            time.sleep(2) # Pequena pausa entre buscas para não ser bloqueado
        except Exception as e:
            print(f"❌ Erro ao processar o segmento {segmento}: {e}")

    driver.quit()

    # 2. CONSOLIDAÇÃO E ORDENAÇÃO (O "CALOR" DAS OFERTAS)
    if lista_consolidada:
        df_final = pd.concat(lista_consolidada, ignore_index=True)

        # Ordenação Decrescente: 
        # Como o Ranking Orgânico já classifica por demanda, 
        # garantimos que os 'Muito Orgânicos' de todas as categorias fiquem no topo.
        df_final = df_final.sort_values(by="Prioridade", ascending=False)

        # 3. SALVAMENTO PADRÃO ABNT/EXCEL BRASIL
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "VARREDURA_GLOBAL_OFERTAS_QUENTES.csv"
        file_path = os.path.join(script_dir, filename)
        
        # sep=';' e encoding='utf-8-sig' garantem a compatibilidade ABNT no Excel
        df_final.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"\n🏆 SUCESSO! Relatório Global gerado com {len(df_final)} produtos.")
        print(f"📍 Local: {file_path}")
    else:
        print("\n⚠️ Nenhum dado foi coletado na varredura.")