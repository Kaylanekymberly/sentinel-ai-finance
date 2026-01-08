import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class PriceFetcher:
    """
    Classe que busca preços históricos de ações brasileiras
    """
    
    def __init__(self):
        print("📈 Price Fetcher inicializado!")
    
    def buscar_preco_acao(self, ticker, periodo='1mo'):
        """
        Busca dados históricos de uma ação
        
        Parâmetros:
        ticker (str): Código da ação (ex: 'PETR4.SA')
        periodo (str): Período ('1d', '5d', '1mo', '3mo', '1y')
        
        Retorna:
        DataFrame: Dados históricos (data, abertura, fechamento, volume, etc)
        """
        print(f"🔍 Buscando dados de {ticker}...")
        
        try:
            # Adiciona .SA para ações brasileiras (B3)
            if not ticker.endswith('.SA'):
                ticker_yahoo = f"{ticker}.SA"
            else:
                ticker_yahoo = ticker
            
            # Busca dados no Yahoo Finance
            acao = yf.Ticker(ticker_yahoo)
            df = acao.history(period=periodo)
            
            if df.empty:
                print(f"⚠️ Nenhum dado encontrado para {ticker}")
                return None
            
            # Reseta index para ter a data como coluna
            df = df.reset_index()
            
            # Adiciona coluna com ticker original
            df['ticker'] = ticker.replace('.SA', '')
            
            # Calcula variação percentual diária
            df['variacao_pct'] = df['Close'].pct_change() * 100
            
            # Renomeia colunas para português
            df = df.rename(columns={
                'Date': 'data',
                'Open': 'abertura',
                'High': 'maxima',
                'Low': 'minima',
                'Close': 'fechamento',
                'Volume': 'volume'
            })
            
            # Seleciona colunas importantes
            df = df[['data', 'ticker', 'abertura', 'fechamento', 'maxima', 
                    'minima', 'volume', 'variacao_pct']]
            
            print(f"✅ {len(df)} dias de dados obtidos!")
            return df
            
        except Exception as e:
            print(f"❌ Erro ao buscar {ticker}: {e}")
            return None
    
    def buscar_multiplas_acoes(self, tickers_list, periodo='1mo'):
        """
        Busca dados de múltiplas ações
        
        Parâmetros:
        tickers_list (list): Lista de tickers ['PETR4', 'VALE3']
        periodo (str): Período de dados
        
        Retorna:
        DataFrame: Todos os dados concatenados
        """
        todos_dados = []
        
        for ticker in tickers_list:
            df = self.buscar_preco_acao(ticker, periodo)
            if df is not None:
                todos_dados.append(df)
            time.sleep(1)  # Pausa de 1 segundo entre requisições
        
        if todos_dados:
            df_completo = pd.concat(todos_dados, ignore_index=True)
            print(f"\n🎉 Total: {len(df_completo)} registros de {len(tickers_list)} ações")
            return df_completo
        else:
            print("⚠️ Nenhum dado foi coletado")
            return None
    
    def calcular_variacao_periodo(self, ticker, data_inicio, data_fim):
        """
        Calcula a variação de preço entre duas datas
        
        Parâmetros:
        ticker (str): Código da ação
        data_inicio (str): Data inicial 'YYYY-MM-DD'
        data_fim (str): Data final 'YYYY-MM-DD'
        
        Retorna:
        dict: Variação percentual e absoluta
        """
        try:
            ticker_yahoo = f"{ticker}.SA" if not ticker.endswith('.SA') else ticker
            acao = yf.Ticker(ticker_yahoo)
            
            # Busca dados do período
            df = acao.history(start=data_inicio, end=data_fim)
            
            if len(df) < 2:
                return None
            
            preco_inicial = df['Close'].iloc[0]
            preco_final = df['Close'].iloc[-1]
            variacao_pct = ((preco_final - preco_inicial) / preco_inicial) * 100
            variacao_abs = preco_final - preco_inicial
            
            return {
                'ticker': ticker.replace('.SA', ''),
                'preco_inicial': round(preco_inicial, 2),
                'preco_final': round(preco_final, 2),
                'variacao_pct': round(variacao_pct, 2),
                'variacao_abs': round(variacao_abs, 2),
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular variação: {e}")
            return None
    
    def salvar_dados(self, df, nome_arquivo='data/precos.csv'):
        """
        Salva dados de preços em CSV
        """
        if df is not None and not df.empty:
            df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
            print(f"💾 Dados salvos em {nome_arquivo}")
        else:
            print("⚠️ Nenhum dado para salvar")
    
    def resumo_precos(self, df):
        """
        Mostra resumo estatístico dos preços
        """
        print("\n📊 RESUMO DOS PREÇOS:\n")
        
        for ticker in df['ticker'].unique():
            df_ticker = df[df['ticker'] == ticker]
            
            preco_atual = df_ticker['fechamento'].iloc[-1]
            preco_minimo = df_ticker['minima'].min()
            preco_maximo = df_ticker['maxima'].max()
            variacao_media = df_ticker['variacao_pct'].mean()
            
            print(f"{ticker}:")
            print(f"  Preço atual: R$ {preco_atual:.2f}")
            print(f"  Mínima do período: R$ {preco_minimo:.2f}")
            print(f"  Máxima do período: R$ {preco_maximo:.2f}")
            print(f"  Variação média diária: {variacao_media:.2f}%")
            print()


# TESTE DO PRICE FETCHER
if __name__ == "__main__":
    # Criar instância
    fetcher = PriceFetcher()
    
    # Lista de ações
    acoes = ['PETR4', 'VALE3', 'ITUB4']
    
    print("="*60)
    print("TESTE 1: Buscar dados históricos (último mês)")
    print("="*60)
    
    # Buscar dados
    df_precos = fetcher.buscar_multiplas_acoes(acoes, periodo='1mo')
    
    if df_precos is not None:
        # Mostrar resumo
        fetcher.resumo_precos(df_precos)
        
        # Salvar
        fetcher.salvar_dados(df_precos)
        
        # Mostrar amostra
        print("\n📋 AMOSTRA DOS DADOS:")
        print(df_precos.head(10).to_string(index=False))
    
    print("\n" + "="*60)
    print("TESTE 2: Calcular variação entre datas específicas")
    print("="*60)
    
    # Exemplo: variação dos últimos 7 dias
    data_fim = datetime.now().strftime('%Y-%m-%d')
    data_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    for ticker in acoes:
        resultado = fetcher.calcular_variacao_periodo(ticker, data_inicio, data_fim)
        if resultado:
            print(f"\n{resultado['ticker']}:")
            print(f"  {resultado['data_inicio']} → {resultado['data_fim']}")
            print(f"  R$ {resultado['preco_inicial']} → R$ {resultado['preco_final']}")
            print(f"  Variação: {resultado['variacao_pct']}% ({resultado['variacao_abs']:+.2f})")