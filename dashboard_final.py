import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
from utils import get_category

# 1. Configuração de Layout App Nu
st.set_page_config(page_title="Nu Finanças", layout="centered", page_icon="💜")

# Estilização Oficial Nubank Dark Mode
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Ocultar elementos nativos do Streamlit para simular um App nativo */
    header, footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden; }
    
    /* Escala Totalmente Preta do App Nubank */
    .stApp { background-color: #000000; font-family: 'Inter', sans-serif; }
    
    /* Letras e Títulos Nubank */
    p, span, div, h1, h2, h3, h4, h5 { color: #ffffff; }
    
    /* "Cartão" de Fatura do Nubank */
    .nu-card {
        background-color: #1A1A1A;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .nu-subtitle {
        color: #8A05BE !important; /* Nu Purple Clássico */
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    
    .nu-balance {
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -2px;
        margin-bottom: 4px;
    }
    
    .nu-transaction {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 0;
        border-bottom: 1px solid #222222;
    }
    
    .nu-desc { font-weight: 600; font-size: 1.1rem; }
    .nu-cat { color: #888888 !important; font-size: 0.9rem; margin-top: 4px; }
    .nu-val { font-weight: 600; font-size: 1.1rem; }
    
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
            
            # Categorização unificada vinda do utils.py
            cat = get_category(memo, amt)
            
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



# --- SIDEBAR: MENU DE APP ---
st.sidebar.title("⚙️ Configurar Fatura")

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

# 4. Limite de Gastos (Nu Analytics)
limite_mensal = st.sidebar.number_input("🎯 Definir Limite Mensal (R$)", min_value=100.0, max_value=50000.0, value=4250.0, step=100.0)

# --- APLICAÇÃO DOS FILTROS ---
meses_selecionados_dt = [meses_formatados[opcoes_meses.index(m)] for m in filtro_mes]
df_filtered = df[
    (df['Mês'].isin(meses_selecionados_dt)) & 
    (df['Categoria'].isin(filtro_cat)) & 
    (df['Valor'].between(filtro_valor[0], filtro_valor[1]))
]

# --- TELA PRINCIPAL NUBANK (ANALYTICS) ---
mes_max = df_filtered['Mês'].max() if not df_filtered.empty else None
alerta_html = ""
dica = "📊 Ritmo de gastos sob controle. Mantenha o equilíbrio no uso do cartão."
perc_gasto = 0
total_gasto = 0
mes_atual = 'Mês'

if pd.notna(mes_max):
    total_gasto = df_filtered[df_filtered['Mês'] == mes_max]['Valor'].sum()
    mes_atual = mes_max.strftime('%b').title()
    
    # Motor de Comparação: Buscando o mês anterior real no DF completo
    meses_anteriores = sorted([m for m in df['Mês'].unique() if m < mes_max])
    if meses_anteriores:
        mes_ant = meses_anteriores[-1]
        gasto_anterior = df[(df['Mês'] == mes_ant)]['Valor'].sum()
        variacao_raw = total_gasto - gasto_anterior
        variacao_pct = (variacao_raw / gasto_anterior) * 100 if gasto_anterior > 0 else 0
        
        if variacao_pct > 0:
            alerta_html = f'<span style="color: #FF1744; font-weight: 600; font-size: 0.9rem;">↑ {variacao_pct:.1f}% vs. mês anterior</span>'
        else:
            alerta_html = f'<span style="color: #04D361; font-weight: 600; font-size: 0.9rem;">↓ {abs(variacao_pct):.1f}% vs. mês anterior</span>'
            dica = "✅ Ótimo trabalho! Você reduziu seus gastos nesta fatura em relação à fatura fechada."

# Inteligência de Limite e Barra de Progresso
if limite_mensal > 0:
    perc_gasto = (total_gasto / limite_mensal) * 100
    cor_barra = "#8A05BE" if perc_gasto <= 80 else "#FF1744"
    limite_disponivel = max(0, limite_mensal - total_gasto)
    
    if perc_gasto > 90:
        dica = f"🚨 Atenção máxima: Você já comprometeu {perc_gasto:.1f}% do seu limite estabelecido. Risco de estourar o orçamento!"
    elif perc_gasto > 75:
        dica = f"⚠️ Cuidado: O espaço na fatura está apertando. Você já consumiu mais de 75% da meta estipulada."
else:
    cor_barra = "#8A05BE"
    limite_disponivel = 0

# Construção do Componente Dinâmico Nu Card
st.markdown(f"""<div class="nu-card">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div>
<div class="nu-subtitle">Fatura atual ({mes_atual})</div>
<div class="nu-balance">R$ {total_gasto:,.2f}</div>
<div style="color: #888; font-size: 1rem; margin-bottom: 12px;">Limite disponível R$ {limite_disponivel:,.2f}</div>
</div>
<div style="text-align: right; margin-top: 5px;">{alerta_html}</div>
</div>
<div style="margin-top: 8px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
<span style="color: #888; font-size: 0.9rem;">Meta: R$ {limite_mensal:,.2f}</span>
<span style="color: {cor_barra}; font-size: 0.9rem; font-weight: bold;">{perc_gasto:.1f}% usado</span>
</div>
<div style="width: 100%; background-color: #222222; border-radius: 8px; height: 8px; overflow: hidden;">
<div style="width: {min(perc_gasto, 100)}%; background-color: {cor_barra}; height: 100%; border-radius: 8px;"></div>
</div>
</div>
</div>

<div class="nu-card" style="padding: 16px; background-color: #1A1A1A; border-left: 4px solid #8A05BE; display: flex; align-items: center; gap: 15px;">
<div style="font-size: 2rem;">💡</div>
<div>
<div style="color: #FFFFFF; font-weight: 600; font-size: 1.05rem; margin-bottom: 2px;">Insight Analítico</div> 
<div style="color: #BBBBBB; font-size: 0.95rem;">{dica}</div>
</div>
</div>""", unsafe_allow_html=True)

cores_nubank = ['#8A05BE', '#9C27B0', '#BA68C8', '#CE93D8', '#E1BEE7', '#F3E5F5', '#04D361', '#1BA5FA']

st.markdown('<div class="nu-subtitle" style="margin-top: 40px; font-size: 1.3rem;">Análise das categorias</div>', unsafe_allow_html=True)

fig_pie = px.pie(df_filtered, values='Valor', names='Categoria', hole=.75, 
                 color_discrete_sequence=cores_nubank)
fig_pie.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color="white"),
    margin=dict(t=10, b=10, l=0, r=0),
    showlegend=True
)
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="nu-subtitle" style="margin-top: 40px; font-size: 1.3rem;">Evolução da Fatura</div>', unsafe_allow_html=True)
df_trend = df_filtered.groupby(['Mês', 'Categoria'])['Valor'].sum().reset_index()
df_trend['Mês_Formatado'] = df_trend['Mês'].dt.strftime('%b')
df_trend = df_trend.sort_values('Mês')

fig_trend = px.bar(
    df_trend, 
    x='Mês_Formatado', 
    y='Valor', 
    color='Categoria',
    color_discrete_sequence=cores_nubank
)

fig_trend.update_layout(
    xaxis_title=None, 
    yaxis_title=None,
    barmode='stack',
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="white"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False, visible=False),
    showlegend=False,
    margin=dict(t=10, b=10, l=0, r=0)
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown('<div class="nu-subtitle" style="margin-top: 40px; font-size: 1.3rem;">Histórico de compras</div>', unsafe_allow_html=True)

# Simular a lista de transações do app num loop HTML para parecer Mobile!
transacoes_html = ""
for _, row in df_filtered.sort_values('Data', ascending=False).iterrows():
    # Usando string segura para não quebrar a formatação
    desc = str(row['Descrição']).title()
    cat = str(row['Categoria'])
    data_formatada = row['Data'].strftime('%d %b')
    valor_formatado = f"{row['Valor']:,.2f}"
    
    # Alinhando a string à esquerda (sem os 4 espaços no começo de cada linha)
    # Isso impede que a engine de Markdown do Streamlit ache que isso é um "bloco de código"
    transacoes_html += f"""<div class="nu-transaction">
    <div>
        <div class="nu-desc">{desc}</div>
        <div class="nu-cat">{data_formatada} • {cat}</div>
    </div>
    <div class="nu-val">R$ {valor_formatado}</div>
</div>"""

st.markdown(f'<div style="margin-bottom: 50px;">{transacoes_html}</div>', unsafe_allow_html=True)