import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

class NoticiasScraper:
    def __init__(self):
        # Lista de User-Agents para o site não nos bloquear
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]
        self.noticias = []

    def get_headers(self):
        return {'User-Agent': random.choice(self.user_agents)}

    def buscar_infomoney(self, ticker, num_paginas=2):
        """ Busca notícias no InfoMoney com suporte a múltiplas páginas (Histórico) """
        print(f"🔍 [InfoMoney] Buscando histórico de {ticker}...")
        
        for pagina in range(1, num_paginas + 1):
            try:
                # A URL muda dependendo da página para pegar notícias antigas
                url = f"https://www.infomoney.com.br/busca/?q={ticker}&page={pagina}"
                response = requests.get(url, headers=self.get_headers(), timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    artigos = soup.find_all('article') 
                    
                    if not artigos:
                        break # Se não tem artigo na página, para de buscar

                    for artigo in artigos:
                        titulo_tag = artigo.find('h2') or artigo.find('h3')
                        if titulo_tag:
                            titulo = titulo_tag.get_text(strip=True)
                            link = artigo.find('a')['href'] if artigo.find('a') else ""
                            data_tag = artigo.find('time')
                            data = data_tag.get_text(strip=True) if data_tag else "Data antiga"
                            
                            self.noticias.append({
                                'ticker': ticker,
                                'titulo': titulo,
                                'link': link,
                                'data': data,
                                'fonte': 'InfoMoney'
                            })
                    print(f"  Página {pagina}: OK")
                
                time.sleep(random.uniform(1, 3)) # Pausa humana para não ser banido
            except Exception as e:
                print(f"  Erro na página {pagina}: {e}")

    def buscar_g1(self, ticker):
        """ Fonte extra: G1 Economia """
        print(f"🔍 [G1] Buscando notícias de {ticker}...")
        try:
            url = f"https://g1.globo.com/busca/?q={ticker}"
            response = requests.get(url, headers=self.get_headers(), timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # No G1 as notícias ficam em classes 'content-text__title'
            titulos = soup.find_all('div', class_='widget--info__text-container', limit=5)
            
            for item in titulos:
                titulo = item.find('div', class_='widget--info__title').get_text(strip=True)
                link = "https:" + item.find('a')['href']
                self.noticias.append({
                    'ticker': ticker,
                    'titulo': titulo,
                    'link': link,
                    'data': datetime.now().strftime('%d/%m/%Y'),
                    'fonte': 'G1'
                })
        except Exception as e:
            print(f"  Erro no G1: {e}")

    def salvar_dados(self):
        if self.noticias:
            df = pd.DataFrame(self.noticias)
            # Remove notícias duplicadas (títulos iguais)
            df = df.drop_duplicates(subset=['titulo'])
            df.to_csv('data/noticias.csv', index=False, encoding='utf-8-sig')
            print(f"\n✅ Sucesso! {len(df)} notícias únicas salvas em data/noticias.csv")
        else:
            print("\n❌ Nenhuma notícia encontrada.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    scraper = NoticiasScraper()
    ativos = ['PETR4', 'VALE3', 'ITUB4']
    
    for ativo in ativos:
        scraper.buscar_infomoney(ativo, num_paginas=3) # Busca até a página 3 (volta no tempo)
        scraper.buscar_g1(ativo) # Tenta também no G1
        
    scraper.salvar_dados()