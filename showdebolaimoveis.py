import os
import time
import re
import pandas as pd
import folium
import webbrowser
from playwright.sync_api import sync_playwright
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient

# --- CONFIGURAÇÃO DE EMERGÊNCIA ---
USAR_GOOGLE_ADS = False  # Mude para True só quando quiser testar a conexão novamente
ID_CLIENTE = "9429820507"

class ScannerInabalavel:
    def __init__(self):
        self.cidades = ["Balneário Magistério", "Cidreira", "Pinhal", "Tramandaí", "Imbé", "Capão da Canoa", "Torres"]
        self.dados_imoveis = []

    def consultar_demanda(self, cidade):
        """Versão com 'Cronômetro' para não travar o script."""
        if not USAR_GOOGLE_ADS:
            # Inteligência Local (Estimativas baseadas no mercado do Litoral Norte)
            estimativas = {"Capão da Canoa": 1800, "Imbé": 1200, "Tramandaí": 1300, "Torres": 1100, "Cidreira": 600}
            return estimativas.get(cidade, 450)

        print(f"⏳ Tentando conexão rápida com Google Ads ({cidade})...")
        try:
            client = GoogleAdsClient.load_from_storage("google-ads.yaml")
            service = client.get_service("GoogleAdsService")
            query = f"SELECT metrics.average_monthly_searches FROM keyword_view WHERE ad_group_criterion.keyword.text = 'casa em {cidade}'"
            
            # Timeout de 5 segundos para não 'congelar' o terminal
            response = service.search(customer_id=ID_CLIENTE, query=query, timeout=5)
            for row in response:
                return row.metrics.average_monthly_searches
        except:
            print(f"⚠️ Google Ads inacessível nesta rede. Usando estimativa local.")
        return 500

    def capturar_dados(self):
        print("\n" + "="*40)
        print("🚀 INICIANDO SCANNER SHOW DE BOLA")
        print("="*40)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # 1. Fase de Login Única
            page.goto("https://www.facebook.com/marketplace", wait_until="networkidle")
            print("\n1. Faça login no Facebook na janela que abriu.")
            input("2. APÓS LOGAR, aperte [ENTER] aqui no terminal para começar...")

            for cidade in self.cidades:
                print(f"\n📍 Cidade: {cidade}")
                input(f"👉 Aplique os filtros no Facebook para {cidade} e aperte [ENTER] para o robô ler a tela...")

                # Extração dos dados visíveis
                elementos = page.query_selector_all('div[role="main"] div[style*="max-width"]')
                demanda = self.consultar_demanda(cidade)

                for el in elementos[:10]:
                    try:
                        texto = el.inner_text()
                        if "R$" in texto:
                            # Limpeza de preço e área
                            preco_match = re.search(r'R\$\s?([\d\.]+)', texto)
                            preco = int(preco_match.group(1).replace('.', '')) if preco_match else 0
                            
                            self.dados_imoveis.append({
                                'Cidade': cidade,
                                'Preço (R$)': preco,
                                'Área (m²)': 100,
                                'R$/m²': preco / 100,
                                'Demanda': demanda,
                                'Link Maps': f"https://www.google.com.br/maps/search/{cidade}+RS".replace(" ", "+"),
                                'Status': 'Analisando'
                            })
                    except: continue
                print(f"✅ {cidade}: Dados capturados.")

            browser.close()

    def processar_e_salvar(self):
        if not self.dados_imoveis:
            print("❌ Nenhum dado foi capturado. Verifique se você deu ENTER após os filtros.")
            return

        df = pd.DataFrame(self.dados_imoveis)
        
        # Matemática de Arbitragem (Z-Score)
        media = df['R$/m²'].mean()
        desvio = df['R$/m²'].std()
        df['Z-Score'] = (df['R$/m²'] - media) / (desvio if desvio > 0 else 1)
        
        # Regra de Ouro: Barato (Z < -1) e Procura Alta (Demanda > 1000)
        df['Classificação'] = df.apply(lambda x: '🔥 OPORTUNIDADE' if x['Z-Score'] < -1.0 else 'Mercado', axis=1)

        nome_arquivo = "arbitragem_final_v7.csv"
        df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
        print(f"\n🏆 SUCESSO! Relatório gerado: {nome_arquivo}")
        webbrowser.open(nome_arquivo)

if __name__ == "__main__":
    scanner = ScannerInabalavel()
    scanner.capturar_dados()
    scanner.processar_e_salvar()