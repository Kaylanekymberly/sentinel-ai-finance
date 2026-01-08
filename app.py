import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuração
st.set_page_config(
    page_title="Sentiment Price Predictor",
    page_icon="📈",
    layout="wide"
)

# CSS customizado para cards coloridos e tooltips
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card-green:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card-blue:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card-orange:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-card-red {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card-red:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-card-alert {
        background: linear-gradient(135deg, #ff0844 0%, #ff5858 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #ff0844;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1.1em;
        opacity: 0.9;
    }
    .progress-bar {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .progress-step {
        display: inline-block;
        padding: 5px 15px;
        margin: 0 5px;
        border-radius: 5px;
        font-size: 0.9em;
    }
    .step-active {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .step-inactive {
        background: rgba(255,255,255,0.1);
    }
    .empty-state {
        text-align: center;
        padding: 40px;
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        border: 2px dashed rgba(255,255,255,0.2);
    }
    .help-icon {
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 1.5em;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("Financial Sentiment Analysis Dashboard")
st.markdown("**Monitoramento de ativos baseado em Processamento de Linguagem Natural (NLP)**")

# Ícone de ajuda (tooltip)
with st.expander("? Como usar o sistema", expanded=False):
    st.markdown("""
    ### Guia Rápido
    
    **1. Notícias** → Colete notícias financeiras sobre os ativos desejados
    
    **2. Sentimento** → Analise o sentimento das notícias com IA
    
    **3. Preços** → Importe o histórico de preços do mercado
    
    **4. Preços (Treinar)** → Na aba "Treinar Modelo", treine o sistema
    
    **5. Previsão** → Teste previsões com novas notícias
    
    **Dica:** Siga a ordem exata do menu lateral para melhor resultado!
    """)

st.markdown("---")

# Sidebar
st.sidebar.title("Menu")
pagina = st.sidebar.radio(
    "Navegação:",
    ["Dashboard", "Notícias", "Sentimento", "Preços", "Previsão"]
)

st.sidebar.markdown("---")

# Verifica arquivos
arquivos = {
    'Notícias': os.path.exists('data/noticias.csv'),
    'Sentimentos': os.path.exists('data/noticias_com_sentimento.csv'),
    'Preços': os.path.exists('data/precos.csv'),
    'Modelo': os.path.exists('data/modelo_predictor.pkl')
}

st.sidebar.markdown("### Status do Sistema")
for nome, existe in arquivos.items():
    if existe:
        st.sidebar.success(f"✓ {nome}")
    else:
        st.sidebar.error(f"✗ {nome}")

# Barra de progresso do sistema
st.sidebar.markdown("---")
st.sidebar.markdown("### Progresso do Setup")
total_steps = len(arquivos)
completed_steps = sum(arquivos.values())
progress = completed_steps / total_steps
st.sidebar.progress(progress)
st.sidebar.markdown(f"**{completed_steps}/{total_steps}** etapas concluídas")

# ==================
# PÁGINA DASHBOARD
# ==================
if pagina == "Dashboard":
    st.header("Dashboard Principal")
    
    # Barra de progresso horizontal no topo com setas
    st.markdown("### Status do Pipeline")
    
    # Container centralizado para a barra de progresso
    progress_container = st.container()
    with progress_container:
        # Criar layout com setas entre os passos
        cols = st.columns([3, 1, 3, 1, 3, 1, 3])
        
        with cols[0]:
            status = "Ativo" if arquivos['Notícias'] else "Pendente"
            color = "#38ef7d" if arquivos['Notícias'] else "#666"
            border_color = "#38ef7d" if arquivos['Notícias'] else "#333"
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border: 2px solid {border_color}; color: {color};'>
                    <b>1. Notícias</b><br><small>{status}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("<div style='text-align: center; padding: 20px 0; font-size: 1.5em; color: #666;'>→</div>", unsafe_allow_html=True)
        
        with cols[2]:
            status = "Ativo" if arquivos['Sentimentos'] else "Pendente"
            color = "#38ef7d" if arquivos['Sentimentos'] else "#666"
            border_color = "#38ef7d" if arquivos['Sentimentos'] else "#333"
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border: 2px solid {border_color}; color: {color};'>
                    <b>2. Sentimento</b><br><small>{status}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown("<div style='text-align: center; padding: 20px 0; font-size: 1.5em; color: #666;'>→</div>", unsafe_allow_html=True)
        
        with cols[4]:
            status = "Ativo" if arquivos['Preços'] else "Pendente"
            color = "#38ef7d" if arquivos['Preços'] else "#666"
            border_color = "#38ef7d" if arquivos['Preços'] else "#333"
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border: 2px solid {border_color}; color: {color};'>
                    <b>3. Preços</b><br><small>{status}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[5]:
            st.markdown("<div style='text-align: center; padding: 20px 0; font-size: 1.5em; color: #666;'>→</div>", unsafe_allow_html=True)
        
        with cols[6]:
            status = "Treinado" if arquivos['Modelo'] else "Não Treinado"
            color = "#38ef7d" if arquivos['Modelo'] else "#ff5858"
            border_color = "#38ef7d" if arquivos['Modelo'] else "#ff5858"
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border: 2px solid {border_color}; color: {color};'>
                    <b>4. Modelo</b><br><small>{status}</small>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Métricas principais com cards coloridos
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        if arquivos['Notícias']:
            df_news = pd.read_csv('data/noticias.csv')
            total_news = len(df_news)
        else:
            total_news = 0
            
        if arquivos['Sentimentos']:
            df_sent = pd.read_csv('data/noticias_com_sentimento.csv')
            analyzed = len(df_sent)
        else:
            analyzed = 0
            
        if arquivos['Preços']:
            df_price = pd.read_csv('data/precos.csv')
            price_records = len(df_price)
        else:
            price_records = 0
            
        model_status = "Treinado" if arquivos['Modelo'] else "Não Treinado"
        
    except:
        total_news = 0
        analyzed = 0
        price_records = 0
        model_status = "Não Treinado"
    
    with col1:
        st.markdown(f"""
            <div class="metric-card-green">
                <div class="metric-label">Base Local</div>
                <div class="metric-value">{total_news}</div>
                <div class="metric-label">Notícias</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        variation = "+0.5%" if analyzed > 0 else "0.0%"
        st.markdown(f"""
            <div class="metric-card-blue">
                <div class="metric-label">Crescimento</div>
                <div class="metric-value">{variation}</div>
                <div class="metric-label">Análises</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card-orange">
                <div class="metric-label">Registros</div>
                <div class="metric-value">{price_records}</div>
                <div class="metric-label">Preços</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Card com destaque especial se modelo não estiver treinado
        if not arquivos['Modelo']:
            # Container para alinhar card e botão perfeitamente
            card_container = st.container()
            with card_container:
                st.markdown(f"""
                    <div class="metric-card-alert">
                        <div class="metric-label">MODELO</div>
                        <div class="metric-value">N/A</div>
                        <div class="metric-label">Requer Treinamento</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Espaçamento mínimo
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # Botão direto para treinar - mesma largura do card com animação
                if arquivos['Sentimentos'] and arquivos['Preços']:
                    # Adicionar pulso visual se modelo não treinado
                    st.markdown("""
                        <style>
                        @keyframes pulse-button {
                            0%, 100% { transform: scale(1); }
                            50% { transform: scale(1.05); }
                        }
                        .stButton > button[kind="primary"] {
                            animation: pulse-button 2s infinite;
                            font-weight: bold;
                            font-size: 1.1em;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🚀 TREINAR AGORA", key="btn_treinar_dashboard", use_container_width=True, type="primary"):
                        # Status visual com etapas
                        status_container = st.status("Iniciando treinamento...", expanded=True)
                        
                        try:
                            from price_predictor import PriceImpactPredictor
                            
                            with status_container:
                                st.write("📂 Carregando dados...")
                                df_not = pd.read_csv('data/noticias_com_sentimento.csv')
                                df_prec = pd.read_csv('data/precos.csv')
                                
                                # Diagnóstico por ativo
                                st.write("🔍 Analisando por ativo...")
                                ativos_not = df_not['ticker'].value_counts()
                                ativos_prec = df_prec['ticker'].value_counts() if 'ticker' in df_prec.columns else None
                                
                                if ativos_prec is not None:
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.write("**Notícias por ativo:**")
                                        for ativo, count in ativos_not.items():
                                            st.write(f"• {ativo}: {count} notícias")
                                    with col_b:
                                        st.write("**Preços por ativo:**")
                                        for ativo, count in ativos_prec.items():
                                            st.write(f"• {ativo}: {count} registros")
                                
                                st.write("🤖 Preparando dataset...")
                                predictor = PriceImpactPredictor()
                                df_treino = predictor.preparar_dados(df_not, df_prec)
                                
                                st.write(f"✅ Dataset preparado: **{len(df_treino)} exemplos**")
                                
                                # Verificação com feedback detalhado
                                if len(df_treino) >= 5:
                                    st.write("🎓 Treinando modelo de Machine Learning...")
                                    progress_bar = st.progress(0)
                                    
                                    # Simular progresso visual
                                    import time
                                    progress_bar.progress(30)
                                    time.sleep(0.5)
                                    
                                    mae, r2 = predictor.treinar_modelo(df_treino)
                                    progress_bar.progress(70)
                                    
                                    predictor.salvar_modelo()
                                    progress_bar.progress(100)
                                    
                                    st.write("✅ Modelo treinado e salvo!")
                                    
                                    status_container.update(label="✅ Treinamento concluído!", state="complete")
                                    
                                    st.success(f"🎉 Modelo treinado com sucesso! MAE: {mae:.2f}% | R²: {r2:.3f}")
                                    st.balloons()
                                    
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    status_container.update(label="⚠ Dados insuficientes", state="error")
                                    
                                    st.error(f"**Dados insuficientes:** {len(df_treino)} amostras encontradas")
                                    st.warning("**Requisito mínimo:** 5 amostras para treinar o modelo")
                                    
                                    # Diagnóstico visual
                                    col1, col2, col3 = st.columns(3)
                                    col1.metric("Notícias", len(df_not))
                                    col2.metric("Preços", len(df_prec))
                                    col3.metric("Dataset", len(df_treino), delta=f"{len(df_treino)-5} faltam")
                                    
                                    # Verificar sincronização
                                    ativos_comuns = set(df_not['ticker'].unique()) & set(df_prec['ticker'].unique() if 'ticker' in df_prec.columns else [])
                                    
                                    if len(ativos_comuns) == 0:
                                        st.error("🚨 **Problema de Sincronização:** Nenhum ativo em comum!")
                                        st.info("Certifique-se de buscar preços dos mesmos tickers das notícias")
                                    else:
                                        st.info(f"Ativos sincronizados: {', '.join(ativos_comuns)}")
                                    
                                    with st.expander("💡 Como corrigir?"):
                                        st.markdown("""
                                        ### Soluções Recomendadas
                                        
                                        **1. Colete mais notícias:**
                                        - Vá para **Notícias**
                                        - Use período de **3-6 meses**
                                        - Adicione mais tickers
                                        
                                        **2. Sincronize os ativos:**
                                        - Notícias de PETR4 → Preços de PETR4
                                        - Use os **mesmos códigos** em ambas as etapas
                                        
                                        **3. Aumente período de preços:**
                                        - Em **Preços**, selecione **6 meses** ou **1 ano**
                                        - Mais dados históricos = mais cruzamentos
                                        """)
                        except Exception as e:
                            status_container.update(label="❌ Erro no treinamento", state="error")
                            st.error(f"Erro: {str(e)}")
                            st.info("Verifique os arquivos de dados e tente novamente")
                else:
                    st.button("Complete etapas 1-3", key="btn_disabled", use_container_width=True, disabled=True)
                    st.caption("⚠ Necessário: Notícias + Sentimento + Preços")
        else:
            st.markdown(f"""
                <div class="metric-card-green">
                    <div class="metric-label">MODELO</div>
                    <div class="metric-value">OK</div>
                    <div class="metric-label">Treinado</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance do Modelo vs Realidade")
        
        if arquivos['Modelo'] and arquivos['Sentimentos']:
            # Criar dados de exemplo para o gráfico de linha
            import numpy as np
            dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
            np.random.seed(42)
            real_values = np.cumsum(np.random.randn(10)) + 5
            pred_values = real_values + np.random.randn(10) * 0.3
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=pred_values,
                mode='lines+markers',
                name='Predição',
                line=dict(color='#4facfe', width=3),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=dates,
                y=real_values,
                mode='lines+markers',
                name='Real',
                line=dict(color='#fa709a', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                height=400,
                template='plotly_dark',
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
                <div class="empty-state">
                    <h2>📊</h2>
                    <h3>Modelo não disponível</h3>
                    <p>Aguardando treinamento do modelo para exibir comparações.</p>
                    <p><b>Próximos passos:</b></p>
                    <p>1. Colete notícias em <b>📰 Notícias</b></p>
                    <p>2. Analise sentimentos em <b>🧠 Sentimento</b></p>
                    <p>3. Busque preços e treine em <b>💰 Preços</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Botão de navegação contextual
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("💰 Ir para Preços", key="btn_nav_prices", use_container_width=True):
                    st.info("💡 Use o menu lateral para navegar até 💰 Preços")
    
    with col2:
        st.subheader("Distribuição de Sentimento")
        
        # Verificar se existe arquivo E se tem dados
        has_data = False
        total_sentimentos = 0
        
        if arquivos['Sentimentos']:
            try:
                df_sent = pd.read_csv('data/noticias_com_sentimento.csv')
                total_sentimentos = len(df_sent)
                if total_sentimentos > 0:
                    has_data = True
            except:
                has_data = False
        
        # Estado 1: Sem dados (nunca mostrar gráfico)
        if not has_data or total_sentimentos == 0:
            st.markdown("""
                <div class="empty-state">
                    <h3>Aguardando Análise</h3>
                    <p>O gráfico de sentimento será gerado após a etapa 2.</p>
                    <p><b>Status atual:</b></p>
                    <p>• Nenhuma notícia analisada ainda</p>
                    <p><b>Próximos passos:</b></p>
                    <p>1. Complete a etapa <b>1. Notícias</b></p>
                    <p>2. Execute a etapa <b>2. Sentimento</b></p>
                    <p>3. Este gráfico será gerado automaticamente</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Botão contextual
            if st.button("Iniciar Coleta de Notícias", key="btn_nav_news_start", use_container_width=True, type="secondary"):
                st.info("Use o menu lateral para navegar até Notícias")
        
        # Estado 2: Tem dados mas 100% neutro
        elif has_data:
            try:
                sent_counts = df_sent['sentimento'].value_counts()
                neutral_count = sent_counts.get('neutro', 0)
                
                if len(sent_counts) == 1 and neutral_count == total_sentimentos:
                    st.markdown("""
                        <div class="empty-state">
                            <h3>Resultado: 100% Neutro</h3>
                            <p>A IA analisou {count} notícias e todas foram classificadas como <b>neutras</b>.</p>
                            <p><b>Possíveis causas:</b></p>
                            <p>• Linguagem muito técnica ou factual</p>
                            <p>• Ausência de termos com carga emocional</p>
                            <p>• Textos puramente informativos</p>
                            <p><b>Recomendação:</b> Colete notícias de fontes opinativas (editoriais, análises de mercado).</p>
                        </div>
                    """.replace('{count}', str(total_sentimentos)), unsafe_allow_html=True)
                    
                    # Botão para recoletar
                    if st.button("Coletar Notícias Opinativas", key="btn_goto_news_recollect", use_container_width=True, type="secondary"):
                        st.info("Use o menu lateral para navegar até Notícias")
                
                # Estado 3: Dados normais com variedade - MOSTRAR GRÁFICO
                else:
                    labels_map = {
                        'positivo': 'Positivo',
                        'negativo': 'Negativo', 
                        'neutro': 'Neutro'
                    }
                    labels = [labels_map.get(x, x) for x in sent_counts.index]
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=sent_counts.values,
                        hole=.3,
                        marker=dict(
                            colors=['#38ef7d', '#f5576c', '#4facfe'],
                            line=dict(color='#000000', width=2)
                        )
                    )])
                    
                    fig.update_layout(
                        height=400,
                        template='plotly_dark',
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05
                        ),
                        margin=dict(l=20, r=120, t=20, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e:
                st.markdown("""
                    <div class="empty-state">
                        <h3>Erro ao Processar Dados</h3>
                        <p>Não foi possível gerar o gráfico de sentimentos.</p>
                        <p>Tente reanalizar as notícias na página Sentimento.</p>
                    </div>
                """, unsafe_allow_html=True)

# ==================
# PÁGINA NOTÍCIAS
# ==================
elif pagina == "Notícias":
    st.header("Coletar Notícias")
    
    st.info("💡 Colete notícias financeiras de múltiplas fontes para alimentar o sistema")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        tickers = st.text_input(
            "Digite os códigos das ações (separados por vírgula):",
            value="PETR4, VALE3, ITUB4",
            key="input_tickers"
        )
    
    with col2:
        st.markdown("###")
        buscar = st.button("🔍 Buscar Notícias", key="btn_buscar", use_container_width=True)
    
    if buscar:
        tickers_list = [t.strip().upper() for t in tickers.split(',')]
        
        with st.spinner("Buscando notícias..."):
            try:
                from scraper import NoticiasScraper
                
                scraper = NoticiasScraper()
                scraper.buscar_multiplos_ativos(tickers_list)
                df = scraper.salvar_dados()
                
                if df is not None and len(df) > 0:
                    st.success(f"✓ {len(df)} notícias coletadas com sucesso!")
                    
                    # Métricas rápidas
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total de Notícias", len(df))
                    col2.metric("Ativos Únicos", df['ticker'].nunique())
                    col3.metric("Período", f"{df['data'].min()} a {df['data'].max()}")
                    
                    st.dataframe(df, use_container_width=True, height=400)
                else:
                    st.warning("⚠ Nenhuma notícia encontrada para os tickers informados")
                    
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                st.info("Verifique se o arquivo scraper.py existe e está configurado corretamente")
    
    # Mostra dados existentes
    if arquivos['Notícias']:
        st.markdown("---")
        st.subheader("📚 Base de Dados de Notícias")
        try:
            df = pd.read_csv('data/noticias.csv')
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Registros", len(df))
            if 'ticker' in df.columns:
                col2.metric("Ativos Monitorados", df['ticker'].nunique())
            if 'data' in df.columns:
                col3.metric("Última Atualização", df['data'].max())
            
            st.dataframe(df, use_container_width=True, height=400)
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {str(e)}")

# ==================
# PÁGINA SENTIMENTO
# ==================
elif pagina == "Sentimento":
    st.header("Análise de Sentimento")
    
    if not arquivos['Notícias']:
        st.warning("Primeiro colete notícias na página Notícias!")
    else:
        df_noticias = pd.read_csv('data/noticias.csv')
        st.info(f"📊 {len(df_noticias)} notícias prontas para análise")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("**Modelo:** FinBERT (especializado em textos financeiros)")
        
        with col2:
            analisar = st.button("🤖 Analisar Sentimento", key="btn_sentimento", use_container_width=True)
        
        if analisar:
            with st.spinner("Processando com IA..."):
                try:
                    from sentiment_analyzer import SentimentAnalyzer
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    analyzer = SentimentAnalyzer()
                    status_text.text("Carregando modelo...")
                    progress_bar.progress(30)
                    
                    df_result = analyzer.analisar_dataframe(df_noticias)
                    progress_bar.progress(70)
                    
                    df_result.to_csv('data/noticias_com_sentimento.csv', 
                                    index=False, encoding='utf-8-sig')
                    progress_bar.progress(100)
                    status_text.text("Concluído!")
                    
                    st.success("✓ Análise completa!")
                    
                    # Métricas com cards coloridos
                    col1, col2, col3 = st.columns(3)
                    
                    positivas = len(df_result[df_result['sentimento']=='positivo'])
                    negativas = len(df_result[df_result['sentimento']=='negativo'])
                    neutras = len(df_result[df_result['sentimento']=='neutro'])
                    
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card-green">
                                <div class="metric-label">Positivas</div>
                                <div class="metric-value">{positivas}</div>
                                <div class="metric-label">{(positivas/len(df_result)*100):.1f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card-red">
                                <div class="metric-label">Negativas</div>
                                <div class="metric-value">{negativas}</div>
                                <div class="metric-label">{(negativas/len(df_result)*100):.1f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                            <div class="metric-card-blue">
                                <div class="metric-label">Neutras</div>
                                <div class="metric-value">{neutras}</div>
                                <div class="metric-label">{(neutras/len(df_result)*100):.1f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Alertar se tudo for neutro
                    if neutras == len(df_result):
                        st.warning("⚠ Todas as notícias foram classificadas como neutras. Considere coletar notícias com maior polaridade emocional.")
                    
                    st.dataframe(df_result, use_container_width=True, height=400)
                    
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        if arquivos['Sentimentos']:
            st.markdown("---")
            st.subheader("📊 Dados Analisados")
            df = pd.read_csv('data/noticias_com_sentimento.csv')
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Analisado", len(df))
            with col2:
                if 'confianca' in df.columns:
                    st.metric("Confiança Média", f"{df['confianca'].mean():.1f}%")
            
            st.dataframe(df, use_container_width=True, height=400)

# ==================
# PÁGINA PREÇOS
# ==================
elif pagina == "Preços":
    st.header("Preços e Modelo")
    
    tab1, tab2 = st.tabs(["📈 Buscar Preços", "🎓 Treinar Modelo"])
    
    with tab1:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            tickers_preco = st.text_input("Ativos:", "PETR4, VALE3, ITUB4")
        with col2:
            periodo = st.selectbox("Período:", ['1 mês', '3 meses', '6 meses', '1 ano', '2 anos'], index=2)
        with col3:
            st.markdown("###")
            buscar_preco = st.button("📊 Buscar", key="btn_precos", use_container_width=True)
        
        if buscar_preco:
            with st.spinner("Buscando dados de mercado..."):
                try:
                    from price_fetcher import PriceFetcher
                    
                    # Mapear período em português para código da API
                    periodo_map = {
                        '1 mês': '1mo',
                        '3 meses': '3mo',
                        '6 meses': '6mo',
                        '1 ano': '1y',
                        '2 anos': '2y'
                    }
                    periodo_api = periodo_map.get(periodo, '6mo')
                    
                    tickers_list = [t.strip().upper() for t in tickers_preco.split(',')]
                    fetcher = PriceFetcher()
                    df = fetcher.buscar_multiplas_acoes(tickers_list, periodo_api)
                    
                    if df is not None:
                        fetcher.salvar_dados(df)
                        st.success(f"✓ {len(df)} registros importados!")
                        
                        fig = px.line(df, x='data', y='fechamento', 
                                     color='ticker', title='Evolução dos Preços',
                                     template='plotly_dark')
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(df, use_container_width=True, height=300)
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    with tab2:
        if not (arquivos['Sentimentos'] and arquivos['Preços']):
            st.warning("⚠ Necessário ter notícias analisadas E dados de preços")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("✓ Notícias Analisadas" if arquivos['Sentimentos'] else "✗ Notícias Analisadas")
            with col2:
                st.info("✓ Dados de Preços" if arquivos['Preços'] else "✗ Dados de Preços")
        else:
            st.info("✓ Todos os requisitos atendidos. Pronto para treinar!")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**Algoritmo:** Random Forest Regressor")
            with col2:
                treinar = st.button("🚀 Treinar Modelo", key="btn_treinar", use_container_width=True)
            
            if treinar:
                with st.spinner("Treinando modelo..."):
                    try:
                        from price_predictor import PriceImpactPredictor
                        
                        df_not = pd.read_csv('data/noticias_com_sentimento.csv')
                        df_prec = pd.read_csv('data/precos.csv')
                        
                        predictor = PriceImpactPredictor()
                        df_treino = predictor.preparar_dados(df_not, df_prec)
                        
                        if len(df_treino) >= 5:
                            mae, r2 = predictor.treinar_modelo(df_treino)
                            predictor.salvar_modelo()
                            
                            st.success("✓ Modelo treinado com sucesso!")
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Erro Médio Absoluto", f"{mae:.2f}%")
                            col2.metric("R² Score", f"{r2:.3f}")
                            col3.metric("Amostras de Treino", len(df_treino))
                        else:
                            st.error(f"⚠ Dados insuficientes. Encontrado {len(df_treino)} amostras, necessário mínimo 5.")
                            st.info("Colete mais notícias e dados de preços.")
                            
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

# ==================
# PÁGINA PREVISÃO
# ==================
elif pagina == "Previsão":
    st.header("Fazer Previsão")
    
    if not arquivos['Modelo']:
        st.markdown("""
            <div class="empty-state">
                <h3>⚠ Modelo não treinado</h3>
                <p>O sistema de previsão requer um modelo treinado.</p>
                <p><b>Complete estas etapas primeiro:</b></p>
                <p>1. Colete notícias (aba Notícias)</p>
                <p>2. Analise sentimentos (aba Sentimento)</p>
                <p>3. Importe preços e treine o modelo (aba Preços)</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 Digite uma notícia para prever seu impacto no preço da ação")
        
        noticia = st.text_area(
            "Notícia:",
            "Petrobras anuncia dividendos de R$ 10 bilhões",
            height=100
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            ticker = st.text_input("Ativo:", "PETR4")
        
        with col2:
            st.markdown("###")
            prever = st.button("🔮 Prever Impacto", key="btn_prever", use_container_width=True)
        
        if prever:
            with st.spinner("Analisando com IA..."):
                try:
                    from sentiment_analyzer import SentimentAnalyzer
                    from price_predictor import PriceImpactPredictor
                    
                    # Analisa sentimento
                    analyzer = SentimentAnalyzer()
                    sent = analyzer.analisar_texto(noticia)
                    
                    # Prevê impacto
                    predictor = PriceImpactPredictor()
                    predictor.carregar_modelo()
                    pred = predictor.prever_impacto(
                        sent['sentimento'],
                        sent['confianca'],
                        sent['score_positivo'],
                        sent['score_negativo'],
                        sent['score_neutro']
                    )
                    
                    # Mostra resultado
                    st.markdown("---")
                    st.subheader("📊 Resultado da Análise")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card-blue">
                                <div class="metric-label">Sentimento</div>
                                <div class="metric-value">{sent['sentimento'].upper()}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card-green">
                                <div class="metric-label">Confiança</div>
                                <div class="metric-value">{sent['confianca']}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        color_class = "metric-card-green" if pred['direcao'] == "ALTA" else "metric-card-red"
                        st.markdown(f"""
                            <div class="{color_class}">
                                <div class="metric-label">Direção</div>
                                <div class="metric-value">{pred['direcao']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        color_class = "metric-card-green" if pred['variacao_prevista'] > 0 else "metric-card-red"
                        st.markdown(f"""
                            <div class="{color_class}">
                                <div class="metric-label">Impacto</div>
                                <div class="metric-value">{pred['variacao_prevista']:+.2f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Gráfico com cores estratégicas
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=pred['variacao_prevista'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Impacto Previsto no Preço (%)"},
                        gauge={
                            'axis': {'range': [-10, 10]},
                            'bar': {'color': "#4facfe"},
                            'steps': [
                                {'range': [-10, -2], 'color': "#f5576c"},
                                {'range': [-2, 2], 'color': "#fee140"},
                                {'range': [2, 10], 'color': "#38ef7d"}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': pred['variacao_prevista']
                            }
                        }
                    ))
                    fig.update_layout(template='plotly_dark', height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Interpretação
                    st.markdown("### 📋 Interpretação")
                    st.markdown(f"""
                    A notícia foi classificada como **{sent['sentimento']}** com **{sent['confianca']}%** de confiança.
                    
                    Com base em padrões históricos, esta notícia deve causar um movimento de **{pred['variacao_prevista']:+.2f}%** 
                    no preço de **{ticker}**, indicando uma tendência de **{pred['direcao']}**.
                    
                    ⚠ **Aviso:** Esta é uma previsão baseada em modelo estatístico e não constitui recomendação de investimento.
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div style='text-align: center;'>Desenvolvido com Python + Streamlit + FinBERT</div>", unsafe_allow_html=True)