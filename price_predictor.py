import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from datetime import datetime, timedelta

class PriceImpactPredictor:
    """
    Modelo que prevê o impacto de notícias no preço das ações
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        print("🧠 Price Impact Predictor inicializado!")
    
    def preparar_dados(self, df_noticias, df_precos):
        """
        Combina notícias com dados de preço para criar dataset de treino
        
        Parâmetros:
        df_noticias: DataFrame com notícias e sentimentos
        df_precos: DataFrame com preços históricos
        
        Retorna:
        DataFrame: Dataset pronto para treino
        """
        print("🔧 Preparando dados para treino...")
        
        # Converte data para datetime
        df_precos['data'] = pd.to_datetime(df_precos['data'])
        
        # Para cada notícia, busca variação de preço do dia
        dados_treino = []
        
        for idx, noticia in df_noticias.iterrows():
            ticker = noticia['ticker']
            
            # Filtra preços desse ticker
            precos_ticker = df_precos[df_precos['ticker'] == ticker].copy()
            
            if len(precos_ticker) == 0:
                continue
            
            # Pega data mais recente (simulando notícia de hoje)
            # Em produção real, você parsearia a data da notícia
            data_noticia = precos_ticker['data'].max()
            
            # Busca variação do preço após a notícia (próximo dia útil)
            preco_antes = precos_ticker[precos_ticker['data'] <= data_noticia]['fechamento'].iloc[-1]
            
            # Tenta pegar preço do dia seguinte
            proximos_dias = precos_ticker[precos_ticker['data'] > data_noticia]
            if len(proximos_dias) > 0:
                preco_depois = proximos_dias['fechamento'].iloc[0]
                variacao_real = ((preco_depois - preco_antes) / preco_antes) * 100
            else:
                # Se não tem dia seguinte, usa variação do próprio dia
                variacao_real = precos_ticker[precos_ticker['data'] == data_noticia]['variacao_pct'].iloc[-1]
            
            # Cria features (características) para o modelo
            dados_treino.append({
                'ticker': ticker,
                'sentimento': noticia['sentimento'],
                'confianca': noticia['confianca'],
                'score_positivo': noticia['score_positivo'],
                'score_negativo': noticia['score_negativo'],
                'score_neutro': noticia['score_neutro'],
                'variacao_real': variacao_real  # Target (o que queremos prever)
            })
        
        df_treino = pd.DataFrame(dados_treino)
        
        # Codifica sentimento (positivo=1, neutro=0, negativo=-1)
        df_treino['sentimento_encoded'] = df_treino['sentimento'].map({
            'positivo': 1,
            'neutro': 0,
            'negativo': -1
        })
        
        print(f"✅ Dataset preparado: {len(df_treino)} exemplos")
        return df_treino
    
    def treinar_modelo(self, df_treino):
        """
        Treina o modelo de Machine Learning
        """
        print("\n🎓 Treinando modelo...")
        
        # Define features (X) e target (y)
        feature_cols = ['sentimento_encoded', 'confianca', 'score_positivo', 
                       'score_negativo', 'score_neutro']
        
        X = df_treino[feature_cols]
        y = df_treino['variacao_real']
        
        self.feature_names = feature_cols
        
        # Divide em treino e teste (80% treino, 20% teste)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Cria e treina modelo Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,  # 100 árvores
            max_depth=10,
            random_state=42,
            n_jobs=-1  # Usa todos os cores do PC
        )
        
        self.model.fit(X_train, y_train)
        
        # Avalia performance
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Modelo treinado!")
        print(f"📊 Métricas:")
        print(f"   MAE (Erro Médio Absoluto): {mae:.2f}%")
        print(f"   R² Score: {r2:.3f}")
        print(f"\n💡 Interpretação:")
        print(f"   O modelo erra em média {mae:.2f}% na previsão")
        print(f"   R² de {r2:.3f} {'(bom)' if r2 > 0.5 else '(precisa mais dados)'}")
        
        # Mostra importância das features
        importancias = pd.DataFrame({
            'feature': feature_cols,
            'importancia': self.model.feature_importances_
        }).sort_values('importancia', ascending=False)
        
        print(f"\n🔍 Features mais importantes:")
        for _, row in importancias.iterrows():
            print(f"   {row['feature']}: {row['importancia']:.3f}")
        
        return mae, r2
    
    def prever_impacto(self, sentimento, confianca, score_positivo, 
                       score_negativo, score_neutro):
        """
        Prevê o impacto de uma notícia no preço
        
        Retorna:
        dict: Previsão de variação percentual
        """
        if self.model is None:
            print("❌ Modelo não foi treinado ainda!")
            return None
        
        # Codifica sentimento
        sentimento_encoded = {'positivo': 1, 'neutro': 0, 'negativo': -1}[sentimento]
        
        # Prepara features
        features = np.array([[
            sentimento_encoded,
            confianca,
            score_positivo,
            score_negativo,
            score_neutro
        ]])
        
        # Faz previsão
        variacao_prevista = self.model.predict(features)[0]
        
        return {
            'variacao_prevista': round(variacao_prevista, 2),
            'direcao': '📈 ALTA' if variacao_prevista > 0 else '📉 QUEDA',
            'intensidade': abs(variacao_prevista)
        }
    
    def salvar_modelo(self, nome_arquivo='data/modelo_predictor.pkl'):
        """
        Salva o modelo treinado
        """
        if self.model is not None:
            with open(nome_arquivo, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_names': self.feature_names
                }, f)
            print(f"💾 Modelo salvo em {nome_arquivo}")
        else:
            print("⚠️ Nenhum modelo para salvar")
    
    def carregar_modelo(self, nome_arquivo='data/modelo_predictor.pkl'):
        """
        Carrega modelo salvo
        """
        try:
            with open(nome_arquivo, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_names = data['feature_names']
            print(f"✅ Modelo carregado de {nome_arquivo}")
            return True
        except FileNotFoundError:
            print(f"⚠️ Arquivo {nome_arquivo} não encontrado")
            return False


# TESTE DO PREDICTOR
if __name__ == "__main__":
    print("="*60)
    print("TESTE: TREINAMENTO DO MODELO")
    print("="*60)
    
    # Carrega dados
    try:
        df_noticias = pd.read_csv('data/noticias_com_sentimento.csv')
        df_precos = pd.read_csv('data/precos.csv')
        
        print(f"\n📊 Dados carregados:")
        print(f"   Notícias: {len(df_noticias)}")
        print(f"   Preços: {len(df_precos)} registros")
        
        # Cria predictor
        predictor = PriceImpactPredictor()
        
        # Prepara dados
        df_treino = predictor.preparar_dados(df_noticias, df_precos)
        
        # Treina modelo
        if len(df_treino) >= 10:  # Mínimo de dados
            predictor.treinar_modelo(df_treino)
            predictor.salvar_modelo()
            
            # Teste de previsão
            print("\n" + "="*60)
            print("TESTE: PREVISÕES")
            print("="*60)
            
            exemplos = [
                {
                    'sentimento': 'positivo',
                    'confianca': 92.5,
                    'scores': (92.5, 3.2, 4.3),
                    'noticia': 'Petrobras anuncia lucro recorde'
                },
                {
                    'sentimento': 'negativo',
                    'confianca': 88.0,
                    'scores': (5.0, 88.0, 7.0),
                    'noticia': 'Vale enfrenta investigação'
                },
                {
                    'sentimento': 'neutro',
                    'confianca': 65.0,
                    'scores': (20.0, 15.0, 65.0),
                    'noticia': 'Itaú divulga balanço trimestral'
                }
            ]
            
            for ex in exemplos:
                resultado = predictor.prever_impacto(
                    ex['sentimento'],
                    ex['confianca'],
                    ex['scores'][0],
                    ex['scores'][1],
                    ex['scores'][2]
                )
                
                print(f"\n📰 Notícia: {ex['noticia']}")
                print(f"💭 Sentimento: {ex['sentimento'].upper()} ({ex['confianca']}%)")
                print(f"🎯 Previsão: {resultado['direcao']}")
                print(f"📊 Variação esperada: {resultado['variacao_prevista']:+.2f}%")
        
        else:
            print(f"\n⚠️ Poucos dados para treinar ({len(df_treino)} exemplos)")
            print("💡 Execute scraper.py e sentiment_analyzer.py para coletar mais dados")
    
    except FileNotFoundError as e:
        print(f"\n❌ Erro: Arquivo não encontrado - {e}")
        print("\n💡 Execute primeiro:")
        print("   1. python scraper.py")
        print("   2. python sentiment_analyzer.py")
        print("   3. python price_fetcher.py")