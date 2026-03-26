import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import os

# 1. Configuração da Página (Visual Executivo)
st.set_page_config(page_title="Executive Finance Insights", page_icon="📈", layout="wide")

# Estilização Customizada via CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E3A8A; }
    .main { background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

def parse_ofx(file_path):
    with open(file_path, 'r', encoding='iso-8859-1') as f:
        content = f.read()
    transactions = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', content, re.DOTALL)
    data = []
    for trn in transactions:
        memo = re.search(r'<MEMO>(.*?)</MEMO>', trn).group(1)
        amt = float(re.search(r'<TRNAMT>(.*?)</TRNAMT>', trn).group(1))
        date_str = re.search(r'<DTPOSTED>((\d{8}))', trn).group(1)
        
        if amt < 0:
            memo_up = memo.upper()
            if any(k in memo_up for k in ['PETROZATT', 'POSTO', 'RODOVIAS']): cat = 'Mobilidade'
            elif any(k in memo_up for k in ['GOOGLE', 'HBO', 'CLOUD', 'REGISTRO.BR']): cat = 'Assinaturas & Tech'
            elif any(k in memo_up for k in ['HOTEL', 'MORUMBY', 'MOTEIS']): cat = 'Hospedagem'
            elif any(k in memo_up for k in ['SHOPEE', 'MERCADO', 'AMAZON', 'KABUM']): cat = 'Marketplace'
            elif any(k in memo_up for k in ['MODAS', 'OUTLET', 'PIREI']): cat = 'Vestuário'
            else: cat = 'Outros/Diversos'
            
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
all_data = []
for f in files: all_data.extend(parse_ofx(f))
df = pd.DataFrame(all_data)

# --- SIDEBAR (FILTROS) ---
st.sidebar.header("🕹️ Painel de Controle")
st.sidebar.markdown("Use os filtros abaixo para ajustar a visão executiva.")

# Filtro de Mês
meses_disponiveis = sorted(df['Mês'].unique())
meses_formatados = [m.strftime('%B / %Y') for m in meses_disponiveis]
filtro_mes = st.sidebar.multiselect("Filtrar por Período:", meses_formatados, default=meses_formatados)

# Filtro de Categoria
categorias_disponiveis = sorted(df['Categoria'].unique())
filtro_cat = st.sidebar.multiselect("Filtrar por Categoria:", categorias_disponiveis, default=categorias_disponiveis)

# Aplicar Filtros
meses_selecionados_dt = [meses_disponiveis[meses_formatados.index(m)] for m in filtro_mes]
df_filtered = df[(df['Mês'].isin(meses_selecionados_dt)) & (df['Categoria'].isin(filtro_cat))]

# --- DASHBOARD PRINCIPAL ---
st.title("📈 Executive Finance Dashboard")
st.markdown(f"Análise consolidada de **{len(filtro_mes)} meses** de movimentações.")

# Linha de KPIs
col1, col2, col3, col4 = st.columns(4)
total_v = df_filtered['Valor'].sum()
media_transacao = df_filtered['Valor'].mean()
top_cat = df_filtered.groupby('Categoria')['Valor'].sum().idxmax() if not df_filtered.empty else "N/A"

col1.metric("Gasto Total (Periodo)", f"R$ {total_v:,.2f}")
col2.metric("Ticket Médio", f"R$ {media_transacao:,.2f}")
col3.metric("Principal Centro de Custo", top_cat)
col4.metric("Qtd. Transações", len(df_filtered))

st.markdown("---")

# Linha de Gráficos
c1, c2 = st.columns([4, 6])

with c1:
    st.subheader("Concentração por Categoria")
    fig_donut = px.pie(df_filtered, values='Valor', names='Categoria', hole=.5,
                       color_discrete_sequence=px.colors.qualitative.Prism)
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_donut, use_container_width=True)

with c2:
    st.subheader("Evolução de Fluxo de Saída")
    df_evolucao = df_filtered.groupby('Mês')['Valor'].sum().reset_index()
    fig_line = px.area(df_evolucao, x='Mês', y='Valor', 
                       line_shape="spline", markers=True,
                       color_discrete_sequence=['#1E3A8A'])
    fig_line.update_layout(xaxis_title="", yaxis_title="Valor (R$)")
    st.plotly_chart(fig_line, use_container_width=True)

# Tabela Detalhada com Estilo
st.subheader("📋 Detalhamento das Movimentações")
st.dataframe(df_filtered.sort_values('Data', ascending=False), use_container_width=True)

# Rodapé Executivo
st.markdown("---")
st.caption("Dashboard gerado automaticamente via Localhost • Dados processados via Python Pandas & Plotly")