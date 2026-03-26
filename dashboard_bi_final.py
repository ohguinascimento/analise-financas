import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# 1. Configuração de Estilo e Página
st.set_page_config(page_title="Executive Financial BI", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #0047AB; }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

def parse_ofx(file_path):
    with open(file_path, 'r', encoding='iso-8859-1') as f:
        content = f.read()
    transactions = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', content, re.DOTALL)
    data = []
    for trn in transactions:
        amt = float(re.search(r'<TRNAMT>(.*?)</TRNAMT>', trn).group(1))
        memo = re.search(r'<MEMO>(.*?)</MEMO>', trn).group(1).upper()
        date_str = re.search(r'<DTPOSTED>((\d{8}))', trn).group(1)
        
        if amt < 0: # Focar apenas em despesas
            # --- MOTOR DE CATEGORIZAÇÃO EXECUTIVA ---
            if any(k in memo for k in ['WELL HUB', 'GYMPASS', 'WELLHUB']): cat = '🏋️ Saúde & Bem-estar'
            elif any(k in memo for k in ['PETROZATT', 'POSTO', 'RODOVIAS']): cat = '🚗 Mobilidade/Logística'
            elif any(k in memo for k in ['MERCADOLIVRE', 'SHOPEE', 'AMAZON', 'KABUM']): cat = '🛍️ E-commerce/Consumo'
            elif any(k in memo for k in ['GOOGLE', 'HBO', 'RAPIDCLOUD']): cat = '📺 Assinaturas Digitais'
            elif any(k in memo for k in ['HOTEL', 'MORUMBY', 'MOTEIS']): cat = '🏨 Hospedagem/Viagem'
            elif any(k in memo for k in ['MODAS', 'OUTLET', 'PIREI']): cat = '👕 Vestuário'
            else: cat = '📦 Operacional/Outros'
            
            data.append({
                'Data': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"),
                'Mês': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-01"),
                'Descrição': memo,
                'Valor': abs(amt),
                'Categoria': cat
            })
    return data

# Carregamento de Dados
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
if not files:
    st.error("Coloque os ficheiros .ofx na mesma pasta deste script.")
    st.stop()

all_data = []
for f in files: all_data.extend(parse_ofx(f))
df = pd.DataFrame(all_data)

# --- FILTROS LATERAIS ---
st.sidebar.title("💎 BI Executive Control")
meses = sorted(df['Mês'].unique())
filtro_mes = st.sidebar.multiselect("Selecione os Meses:", 
                                    [m.strftime('%m/%Y') for m in meses], 
                                    default=[m.strftime('%m/%Y') for m in meses])

categorias = sorted(df['Categoria'].unique())
filtro_cat = st.sidebar.multiselect("Filtrar Categorias:", categorias, default=categorias)

# Aplicar Filtros
meses_sel = [meses[i] for i, m in enumerate([m.strftime('%m/%Y') for m in meses]) if m in filtro_mes]
df_view = df[(df['Mês'].isin(meses_sel)) & (df['Categoria'].isin(filtro_cat))]

# --- DASHBOARD PRINCIPAL ---
st.title("📈 Relatório de Gestão Financeira")
st.markdown("Consolidado Quadrimestral - Janeiro a Maio 2026")

# KPIs de Resumo
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gasto Total", f"R$ {df_view['Valor'].sum():,.2f}")
c2.metric("Média Mensal", f"R$ {df_view.groupby('Mês')['Valor'].sum().mean():,.2f}")
c3.metric("Investimento Saúde", f"R$ {df_view[df_view['Categoria'] == '🏋️ Saúde & Bem-estar']['Valor'].sum():,.2f}")
c4.metric("E-commerce Total", f"R$ {df_view[df_view['Categoria'] == '🛍️ E-commerce/Consumo']['Valor'].sum():,.2f}")

st.divider()

# Gráficos Analíticos
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Share por Centro de Custo")
    fig_pie = px.pie(df_view, values='Valor', names='Categoria', hole=.4,
                     color_discrete_sequence=px.colors.qualitative.Prism)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    st.subheader("Evolução de Despesas")
    df_evol = df_view.groupby('Mês')['Valor'].sum().reset_index()
    fig_line = px.line(df_evol, x='Mês', y='Valor', markers=True, line_shape="spline",
                       color_discrete_sequence=['#0047AB'])
    st.plotly_chart(fig_line, use_container_width=True)

# Detalhamento Executivo
st.subheader("📋 Auditoria de Lançamentos (Top 15 Maiores)")
st.dataframe(df_view.sort_values('Valor', ascending=False).head(15), use_container_width=True)

st.markdown("---")
st.caption("Fim do Relatório • Gerado via Python Localhost")