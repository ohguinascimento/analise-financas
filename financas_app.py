import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os

# Configuração de App Moderno
st.set_page_config(page_title="Finanças Pro", page_icon="💳", layout="wide")

# CSS para deixar com cara de App
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .css-1r6slb0 { border-radius: 15px; }
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
        
        if amt < 0: # Focar apenas em gastos
            memo_up = memo.upper()
            if any(k in memo_up for k in ['PETROZATT', 'POSTO']): cat = '🚗 Mobilidade'
            elif any(k in memo_up for k in ['GOOGLE', 'HBO', 'CLOUD']): cat = '📺 Assinaturas'
            elif any(k in memo_up for k in ['HOTEL', 'MOTEL']): cat = '🏨 Hospedagem'
            elif any(k in memo_up for k in ['SHOPEE', 'MERCADO', 'AMAZON']): cat = '🛍️ Compras Online'
            elif any(k in memo_up for k in ['MODAS', 'OUTLET', 'PIREI']): cat = '👕 Vestuário'
            else: cat = '🛒 Outros'
            
            data.append({
                'Data': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"),
                'Estabelecimento': memo,
                'Valor': abs(amt),
                'Categoria': cat
            })
    return data

# Processamento
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
all_data = []
for f in files: all_data.extend(parse_ofx(f))
df = pd.DataFrame(all_data)

# --- LAYOUT DO APP ---
st.title("💳 Meu Gerenciador de Cartão")

# Linha de Métricas (Cards)
total_geral = df['Valor'].sum()
maior_gasto = df.groupby('Categoria')['Valor'].sum().max()
cat_top = df.groupby('Categoria')['Valor'].sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("Gasto Total", f"R$ {total_geral:,.2f}")
col2.metric("Categoria Principal", cat_top)
col3.metric("Maior Concentração", f"R$ {maior_gasto:,.2f}")

st.markdown("---")

# Gráficos Dinâmicos
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Gastos por Categoria")
    fig_pie = px.pie(df, values='Valor', names='Categoria', hole=.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("Evolução Mensal")
    df_mes = df.set_index('Data').resample('M')['Valor'].sum().reset_index()
    fig_line = px.line(df_mes, x='Data', y='Valor', markers=True, 
                       line_shape="spline", render_mode="svg")
    st.plotly_chart(fig_line, use_container_width=True)

# Lista Estilizada
st.subheader("Últimas Transações")
st.dataframe(df.sort_values('Data', ascending=False), use_container_width=True)