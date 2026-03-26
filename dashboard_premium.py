import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
import pathlib
from utils import parse_ofx_structured

# 1. Configuração de Interface Premium
st.set_page_config(page_title="Executive BI - Integrated Insights", layout="wide")

# --- CARREGAMENTO E INTEGRAÇÃO ---
current_dir = pathlib.Path('.')
files = list(current_dir.glob('*.ofx'))
all_transactions = []
for f in files:
    all_transactions.extend(parse_ofx_structured(str(f)))

if not all_transactions:
    st.error("Nenhum arquivo .ofx encontrado na pasta raiz!")
    st.stop()

df_fatura = pd.DataFrame(all_transactions)
df_fatura['Valor_Abs'] = df_fatura['Valor'].abs()
df_fatura = df_fatura[df_fatura['Valor'] < 0] # Foco em despesas

# Tentar carregar dados detalhados do ML
ml_file = pathlib.Path('compras_detalhadas_ml.csv')
if ml_file.exists() and ml_file.stat().st_size > 0:
    df_ml_detalhes = pd.read_csv('compras_detalhadas_ml.csv')
    # Limpeza para merge (ex: 'R$ 150,00' -> 150.0)
    df_ml_detalhes['Valor_Float'] = df_ml_detalhes['Valor_ML'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    
    # Integração: Se o valor bater, usamos o nome do produto
    df_final = pd.merge(df_fatura, df_ml_detalhes, left_on='Valor_Abs', right_on='Valor_Float', how='left')
    df_final['Descrição_Final'] = df_final['Produto'].fillna(df_final['Descricao'])
else:
    df_final = df_fatura.copy()
    df_final['Descrição_Final'] = df_final['Descricao']

# --- DASHBOARD UI ---
st.title("🏛️ BI Financeiro: Visão Integrada")

st.sidebar.header("Filtros Executivos")
categorias = st.sidebar.multiselect("Categorias", df_final['Categoria'].unique(), default=df_final['Categoria'].unique())
df_filtered = df_final[df_final['Categoria'].isin(categorias)]

if not df_filtered.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Despesas", f"R$ {df_filtered['Valor_Abs'].sum():,.2f}")
    c2.metric("Média por Item", f"R$ {df_filtered['Valor_Abs'].mean():,.2f}")
    c3.metric("Maior Gasto", df_filtered.loc[df_filtered['Valor_Abs'].idxmax()]['Descrição_Final'])

    st.divider()

    col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Análise de Pareto por Produto/Loja")
    top_itens = df_filtered.groupby('Descrição_Final')['Valor_Abs'].sum().sort_values(ascending=False).head(10)
    fig_bar = px.bar(top_itens, orientation='h', color_value=top_itens.values, color_continuous_scale='Blues')
    st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Share de Carteira")
        fig_donut = px.pie(df_filtered, values='Valor_Abs', names='Categoria', hole=.5)
        st.plotly_chart(fig_donut, use_container_width=True)

    st.subheader("📄 Relatório Detalhado (Dados Integrados)")
    st.dataframe(df_filtered[['Data', 'Descrição_Final', 'Categoria', 'Valor_Abs']].sort_values('Data', ascending=False), use_container_width=True)