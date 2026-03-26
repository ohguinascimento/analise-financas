# 📊 Sistema de Análise de Finanças Pessoais

Este projeto é um ecossistema robusto em Python para extração, processamento e visualização de dados financeiros, integrando faturas bancárias (OFX) e detalhes de compras do Mercado Livre via web scraping.

## 🚀 Como Começar

### 1. Pré-requisitos

Certifique-se de ter o Python 3.10+ instalado.

```bash
# Clone o repositório e entre na pasta
cd analise-financas

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 2. Instalação de Dependências

Instale as bibliotecas necessárias para rodar os extratores e os dashboards:

```bash
pip install streamlit pandas plotly selenium webdriver-manager matplotlib openpyxl
```

## 🛠️ Componentes do Sistema

### 📂 Processamento de Dados (OFX)

1. Coloque seus arquivos exportados do banco (formato `.ofx`) na pasta raiz do projeto.
2. O sistema ignora automaticamente esses arquivos no Git para sua segurança.

### 🛒 Extrator Mercado Livre

Se desejar detalhar suas compras do Mercado Livre:

1. Execute `python extrator_ml_v2.py`.
2. Uma janela do Chrome abrirá; faça login na sua conta.
3. O script gerará o arquivo `compras_detalhadas_ml.csv` com os itens comprados.

### 📈 Dashboards (Streamlit)

Existem diferentes versões do dashboard. A versão mais completa é a **Executive**:

```bash
streamlit run dashboard_final.py
```

Outras opções incluem:

- `dashboard_bi_final.py`: Foco em KPIs executivos.
- `dashboard_premium.py`: Integra os dados do banco com os detalhes do Mercado Livre.

## 📂 Estrutura de Arquivos Principal

- `analise.py`: Script para converter OFX em Excel/CSV de forma rápida.
- `app.py`: Versão simplificada do dashboard.
- `.gitignore`: Configurado para não subir seus dados sensíveis (`.ofx`, `.csv`, `.xlsx`).

## 🔒 Segurança e Privacidade

**Nunca** remova os arquivos `.ofx` ou `.csv` do seu `.gitignore`. Este projeto foi desenhado para rodar localmente, garantindo que seus dados financeiros não sejam expostos em repositórios públicos.

---

_Gerado para análise de finanças pessoais via Python._
