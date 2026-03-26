import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os

# Configuração de Layout BI
st.set_page_config(page_title="Executive Insights - Saúde & E-commerce", layout="wide")

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
            
            # --- NOVA LÓGICA DE CATEGORIZAÇÃO ---
            if any(k in memo for k in ['WELL HUB', 'GYMPASS', 'WELLHUB']): cat = '🏋️ Academia & Saúde'
            elif any(k in memo for k in ['SHOPEE', 'MERCADOLIVRE', 'AMAZON', 'KABUM']): cat = '🛍️ E-commerce'
            elif any(k in memo for k in ['PETROZATT', 'POSTO', 'RODOVIAS']): cat = '🚗 Mobilidade'
            elif any(k in memo for k in ['GOOGLE', 'HBO', 'RAPIDCLOUD']): cat = '📺 Assinaturas'
            elif any(k in memo for k in ['HOTEL', 'MORUMBY', 'MOTEIS']): cat = '🏨 Hospedagem'
            elif any(k in memo for k in ['MODAS', 'OUTLET', 'PIREI']): cat = '👕 Vestuário'
            else: cat = '📦 Outros'
            
            # Sub-classificação de Marketplace para análise profunda
            marketplace = 'Outros'
            if 'SHOPEE' in memo: marketplace = 'Shopee'
            elif 'MERCADOLIVRE' in memo: marketplace = 'Mercado Livre'
            elif 'AMAZON' in memo: marketplace = 'Amazon'
            elif 'KABUM' in memo: marketplace = 'Kabum'

            data.append({
                'Data': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"),
                'Mês': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-01"),
                'Descrição': memo,
                'Valor': abs(amt),
                'Categoria': cat,
                'Marketplace': marketplace
            })
    return data

# Carregamento
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
all_data = []
for f in files: all_data.extend(parse_ofx(f))
df = pd.DataFrame(all_data)

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("🎮 Filtros BI")
meses_opcoes = sorted(df['Mês'].unique())
filtro_mes = st.sidebar.multiselect("Selecione os Meses:", 
                                    [m.strftime('%m/%Y') for m in meses_opcoes], 
                                    default=[m.strftime('%m/%Y') for m in meses_opcoes])

# --- DASHBOARD ---
st.title("📊 Consolidado Executivo: Saúde e Consumo")

# Filtragem de Dados
meses_selecionados = [meses_opcoes[i] for i, m in enumerate([m.strftime('%m/%Y') for m in meses_opcoes]) if m in filtro_mes]
df_view = df[df['Mês'].isin(meses_selecionados)]

# KPIs Superiores
c1, c2, c3 = st.columns(3)
c1.metric("Gasto Saúde (Well Hub)", f"R$ {df_view[df_view['Categoria'] == '🏋️ Academia & Saúde']['Valor'].sum():,.2f}")
c2.metric("Total E-commerce", f"R$ {df_view[df_view['Categoria'] == '🛍️ E-commerce']['Valor'].sum():,.2f}")
c3.metric("Fatura Média Filtrada", f"R$ {df_view.groupby('Mês')['Valor'].sum().mean():,.2f}")

st.divider()

# Gráficos Principais
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Marketplace: Onde você compra mais?")
    df_mkt = df_view[df_view['Categoria'] == '🛍️ E-commerce'].groupby('Marketplace')['Valor'].sum().reset_index()
    fig_mkt = px.bar(df_mkt, x='Marketplace', y='Valor', color='Marketplace', text_auto='.2s',
                     color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_mkt, use_container_width=True)

with col_b:
    st.subheader("Share por Categoria")
    fig_pie = px.pie(df_view, values='Valor', names='Categoria', hole=.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# Análise de Tendência
st.subheader("Evolução Mensal: Saúde vs E-commerce")
trend = df_view[df_view['Categoria'].isin(['🏋️ Academia & Saúde', '🛍️ E-commerce'])].groupby(['Mês', 'Categoria'])['Valor'].sum().reset_index()
fig_trend = px.line(trend, x='Mês', y='Valor', color='Categoria', markers=True, line_shape="spline")
st.plotly_chart(fig_trend, use_container_width=True)

st.subheader("Detalhes das Transações")
st.dataframe(df_view.sort_values('Data', ascending=False), use_container_width=True)