import streamlit as st
import pandas as pd
import plotly.express as px
import reimport os

# Verificação se o arquivo existe e NÃO está vazio
if os.path.exists('compras_detalhadas_ml.csv') and os.stat('compras_detalhadas_ml.csv').st_size > 0:
    try:
        df_ml_detalhes = pd.read_csv('compras_detalhadas_ml.csv')
        # ... resto do código de merge ...
    except Exception as e:
        st.error(f"Erro ao ler detalhes do ML: {e}")
        df_final = df_fatura.copy() # Volta para o básico se falhar
else:
    df_final = df_fatura.copy()
import os

# 1. Configuração de Interface Premium
st.set_page_config(page_title="Executive BI - Integrated Insights", layout="wide")

def parse_ofx(file_path):
    with open(file_path, 'r', encoding='iso-8859-1') as f:
        content = f.read()
    transactions = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', content, re.DOTALL)
    data = []
    for trn in transactions:
        amt = float(re.search(r'<TRNAMT>(.*?)</TRNAMT>', trn).group(1))
        if amt < 0:
            memo = re.search(r'<MEMO>(.*?)</MEMO>', trn).group(1).upper()
            date_str = re.search(r'<DTPOSTED>((\d{8}))', trn).group(1)
            
            # Categorização Inicial
            if any(k in memo for k in ['WELL HUB', 'GYMPASS']): cat = '🏋️ Saúde'
            elif any(k in memo for k in ['MERCADOLIVRE', 'SHOPEE', 'AMAZON']): cat = '🛍️ E-commerce'
            elif any(k in memo for k in ['PETROZATT', 'POSTO']): cat = '🚗 Mobilidade'
            else: cat = '📦 Outros'
            
            data.append({
                'Data': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"),
                'Descrição_Fatura': memo,
                'Valor': abs(amt),
                'Categoria': cat
            })
    return data

# --- CARREGAMENTO E INTEGRAÇÃO ---
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
df_fatura = pd.DataFrame([item for f in files for item in parse_ofx(f)])

# Tentar carregar dados detalhados do ML
if os.path.exists('compras_detalhadas_ml.csv'):
    df_ml_detalhes = pd.read_csv('compras_detalhadas_ml.csv')
    # Limpeza simples para bater os valores (remover R$ e converter para float)
    df_ml_detalhes['Valor_Float'] = df_ml_detalhes['Valor_ML'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    
    # Integração: Se o valor bater, usamos o nome do produto
    df_final = pd.merge(df_fatura, df_ml_detalhes, left_on='Valor', right_on='Valor_Float', how='left')
    df_final['Descrição_Final'] = df_final['Produto'].fillna(df_final['Descrição_Fatura'])
else:
    df_final = df_fatura.copy()
    df_final['Descrição_Final'] = df_final['Descrição_Fatura']

# --- DASHBOARD UI ---
st.title("🏛️ BI Financeiro: Visão Integrada")

# Filtros na Legenda (Sidebar)
st.sidebar.header("Filtros Executivos")
categorias = st.sidebar.multiselect("Categorias", df_final['Categoria'].unique(), default=df_final['Categoria'].unique())
df_filtered = df_final[df_final['Categoria'].isin(categorias)]

# KPIs de Impacto
c1, c2, c3 = st.columns(3)
c1.metric("Investimento em Saúde", f"R$ {df_filtered[df_filtered['Categoria'] == '🏋️ Saúde']['Valor'].sum():,.2f}")
c2.metric("Gasto E-commerce", f"R$ {df_filtered[df_filtered['Categoria'] == '🛍️ E-commerce']['Valor'].sum():,.2f}")
c3.metric("Maior Item Adquirido", df_filtered.loc[df_filtered['Valor'].idxmax()]['Descrição_Final'] if not df_filtered.empty else "N/A")

st.divider()

# Gráficos de Alta Performance
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Análise de Pareto por Produto/Loja")
    # Mostra os nomes reais dos produtos extraídos do ML
    top_itens = df_filtered.groupby('Descrição_Final')['Valor'].sum().sort_values(ascending=False).head(10)
    fig_bar = px.bar(top_itens, orientation='h', color_value=top_itens.values, color_continuous_scale='Blues')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Share de Carteira")
    fig_donut = px.pie(df_filtered, values='Valor', names='Categoria', hole=.5, title="Distribuição Estratégica")
    st.plotly_chart(fig_donut, use_container_width=True)

st.subheader("📄 Relatório Detalhado (Dados Integrados)")
st.dataframe(df_filtered[['Data', 'Descrição_Final', 'Categoria', 'Valor']].sort_values('Data', ascending=False), use_container_width=True)