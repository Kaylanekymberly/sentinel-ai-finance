Documentação de Projeto: Sentinel AI Finance
Este repositório documenta o desenvolvimento de uma aplicação de Inteligência Artificial voltada à análise quantitativa de sentimentos no setor financeiro. O projeto integra modelos de Processamento de Linguagem Natural (NLP) com dashboards interativos para suporte à tomada de decisão.

Competências Técnicas e Pontos Fortes
Implementação de Modelos de NLP: Utilização do FinBERT, um modelo de linguagem especializado, treinado para processar a semântica complexa de relatórios e notícias financeiras.

Arquitetura de Dados: Estruturação de um pipeline que realiza a leitura, tratamento e persistência de dados em arquivos CSV, permitindo a análise histórica e em tempo real.

Interface de Análise (Dashboard): Desenvolvimento de interface via Streamlit, priorizando a usabilidade e a visualização dinâmica de métricas de mercado.

Desafios Técnicos e Gestão de Incidentes
Durante o ciclo de vida do desenvolvimento, foram aplicadas práticas de resolução de problemas e gestão de versão para assegurar a integridade do código:

Recuperação de Desastres via Git: Diante da exclusão acidental do arquivo principal (app.py) durante uma operação de versionamento, foi executada a restauração de arquivos via git checkout a partir de um hash de commit anterior, garantindo a continuidade do projeto.

Depuração e Debugging de Interface: Identificação e correção de erros de sintaxe e argumentos obsoletos (como o ajuste de use_container_width e correção de delimitadores de argumentos) que impactavam diretamente a estabilidade da aplicação em ambiente de produção.

Deploy e Gerenciamento de Dependências: Configuração completa do ambiente de nuvem no Streamlit Cloud, incluindo a gestão de bibliotecas via requirements.txt e sincronização de branches remotas.

Oportunidades de Melhoria e Evolução (Roadmap)
Migração para Fonte de Dados Dinâmica: Transição da leitura de arquivos locais (/data) para a integração com APIs de dados financeiros em tempo real.

Otimização do Versionamento: Refinamento das políticas do .gitignore para assegurar que apenas arquivos de código e configuração sejam versionados, mantendo o repositório em conformidade com as melhores práticas de mercado.
