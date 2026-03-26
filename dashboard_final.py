import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os

# 1. Configuração de Layout Profissional
st.set_page_config(page_title="Finanças Executive", layout="wide", page_icon="📈")

# Estilização para tons de azul escuro e cinza (Executivo)
st.markdown("""
    <style>
    .stMetric { border-left: 5px solid #1E3A8A; background-color: #F1F5F9; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

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
            
            # Categorização
            if any(k in memo for k in ['PETROZATT', 'POSTO', 'RODOVIAS']): cat = 'Mobilidade'
            elif any(k in memo for k in ['GOOGLE', 'HBO', 'RAPIDCLOUD']): cat = 'Assinaturas/SaaS'
            elif any(k in memo for k in ['HOTEL', 'MORUMBY', 'MOTEIS']): cat = 'Hospedagem'
            elif any(k in memo for k in ['SHOPEE', 'MERCADO', 'AMAZON', 'KABUM']): cat = 'E-commerce'
            elif any(k in memo for k in ['MODAS', 'OUTLET', 'PIREI']): cat = 'Vestuário'
            else: cat = 'Outros'
            
            data.append({
                'Data': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"),
                'Mês': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-01"),
                'Descrição': memo,
                'Valor': abs(amt),
                'Categoria': cat
            })
    return data

# Carregamento dos dados
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
all_data = []
for f in files: all_data.extend(parse_ofx(f))
df = pd.DataFrame(all_data)

def categorizar_detalhado(memo):
    m = memo.upper()
    
    # 🏋️ Saúde e Bem-estar
    if any(k in m for k in ['WELL HUB', 'GYMPASS', 'ACADEMIA', 'SMARTFIT']):
        return 'Saúde & Bem-estar'
    
    # 🍔 Alimentação e Conveniência (Refinando o que era 'Outros')
    elif any(k in m for k in ['OXXO', 'IFOOD', 'UBER EATS', 'ZAMP', 'MCDONALD']):
        return 'Alimentação/Conveniência'
    
    # 🍺 Lazer e Social
    elif any(k in m for k in ['GAMA BAR', 'CERVEJARIA', 'ESTABELECIMENTO X']):
        return 'Lazer/Social'
    
    # 🛠️ Serviços e Taxas
    elif any(k in m for k in ['IOF', 'JUROS', 'TARIFA', 'ANUIDADE']):
        return 'Taxas Bancárias'
    
    # ... manter as outras categorias que já criamos (Mobilidade, Vestuário, etc.)
    return 'Outros (Não Classificados)'

# --- SIDEBAR: FILTROS GLOBAIS ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1162/1162251.png", width=100)
st.sidebar.title("Filtros da Base")

# 1. Filtro de Mês (Multiselect)
meses_formatados = sorted(df['Mês'].unique())
opcoes_meses = [m.strftime('%m/%Y') for m in meses_formatados]
filtro_mes = st.sidebar.multiselect("Selecione os Meses:", opcoes_meses, default=opcoes_meses)

# 2. Filtro de Categoria (Multiselect)
categorias = sorted(df['Categoria'].unique())
filtro_cat = st.sidebar.multiselect("Filtrar Categorias:", categorias, default=categorias)

# 3. Filtro de Valor (Slider)
valor_min, valor_max = float(df['Valor'].min()), float(df['Valor'].max())
filtro_valor = st.sidebar.slider("Faixa de Valor (R$):", valor_min, valor_max, (valor_min, valor_max))

# --- APLICAÇÃO DOS FILTROS ---
meses_selecionados_dt = [meses_formatados[opcoes_meses.index(m)] for m in filtro_mes]
df_filtered = df[
    (df['Mês'].isin(meses_selecionados_dt)) & 
    (df['Categoria'].isin(filtro_cat)) & 
    (df['Valor'].between(filtro_valor[0], filtro_valor[1]))
]

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Dashboard Financeiro Executivo")

# Métricas em Colunas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total em Saídas", f"R$ {df_filtered['Valor'].sum():,.2f}")
c2.metric("Média por Compra", f"R$ {df_filtered['Valor'].mean():,.2f}")
c3.metric("Maior Gasto Único", f"R$ {df_filtered['Valor'].max():,.2f}")
c4.metric("Transações", len(df_filtered))

st.divider()

# Gráficos
col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.subheader("Pareto de Gastos (Categoria)")
    fig_bar = px.bar(df_filtered.groupby('Categoria')['Valor'].sum().reset_index().sort_values('Valor'), 
                     x='Valor', y='Categoria', orientation='h', text_auto='.2s',
                     color_discrete_sequence=['#1E3A8A'])
    st.plotly_chart(fig_bar, use_container_width=True)

with col_dir:
    st.subheader("Composição do Budget")
    fig_pie = px.pie(df_filtered, values='Valor', names='Categoria', hole=.4,
                     color_discrete_sequence=px.colors.qualitative.G10)
    st.plotly_chart(fig_pie, use_container_width=True)

# Tabela Interativa
st.subheader("🔍 Auditoria de Lançamentos")
st.dataframe(df_filtered.sort_values('Data', ascending=False), use_container_width=True)

# No Streamlit, adicione isto para investigar o "Outros"
st.subheader("Análise de Resíduos (Categoria: Outros)")
outros_df = df[df['Categoria'] == 'Outros']
top_outros = outros_df.groupby('Descrição')['Valor'].sum().nlargest(5)
st.bar_chart(top_outros)

st.subheader("Análise de Resíduos: O que ainda está em 'Outros'?")
# Filtra apenas o que caiu em outros
df_outros = df_filtered[df_filtered['Categoria'] == 'Outros']

if not df_outros.empty:
    # Mostra os 10 maiores recebedores dentro de 'Outros'
    top_outros = df_outros.groupby('Descrição')['Valor'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_outros)
else:
    st.success("Parabéns! Categoria 'Outros' está vazia ou totalmente filtrada.")