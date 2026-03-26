import streamlit as st
import pandas as pd
import re
import os
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(page_title="Meu Painel Financeiro", layout="wide")

st.title("📊 Análise de Faturas Nubank")
st.markdown("Visualização consolidada de gastos via Localhost")

# Função de processamento (mesma lógica anterior)
def parse_ofx(file_path):
    with open(file_path, 'r', encoding='iso-8859-1') as f:
        content = f.read()
    transactions = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', content, re.DOTALL)
    data = []
    for trn in transactions:
        date_match = re.search(r'<DTPOSTED>((\d{8}))', trn)
        amt_match = re.search(r'<TRNAMT>(.*?)</TRNAMT>', trn)
        memo_match = re.search(r'<MEMO>(.*?)</MEMO>', trn)
        if date_match and amt_match and memo_match:
            date_str = date_match.group(1)
            date = pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
            amount = float(amt_match.group(1))
            memo = memo_match.group(1).upper()
            
            # Categorização rápida
            if any(kw in memo for kw in ['POSTO', 'PETROZATT', 'RODOVIAS']): cat = 'Combustível'
            elif any(kw in memo for kw in ['GOOGLE', 'HBO', 'RAPIDCLOUD']): cat = 'Assinaturas'
            elif any(kw in memo for kw in ['HOTEL', 'MORUMBY', 'MOTEIS']): cat = 'Hospedagem'
            elif any(kw in memo for kw in ['MODAS', 'OUTLET', 'PIREI']): cat = 'Vestuário'
            elif any(kw in memo for kw in ['MERCADOLIVRE', 'SHOPEE', 'AMAZON', 'KABUM']): cat = 'Marketplace'
            elif amount > 0: cat = 'Pagamentos'
            else: cat = 'Outros'
            
            data.append({'Data': date, 'Descrição': memo, 'Valor': amount, 'Categoria': cat})
    return data

# Carregar dados
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
if files:
    all_data = []
    for f in files:
        all_data.extend(parse_ofx(f))
    df = pd.DataFrame(all_data).sort_values('Data')

    # --- INTERFACE WEB ---
    
    # Metricas principais
    gastos_totais = df[df['Valor'] < 0]['Valor'].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total Acumulado", f"R$ {abs(gastos_totais):,.2f}")
    col2.metric("Nº de Transações", len(df))
    col3.metric("Meses Analisados", len(files))

    # Gráfico de Gastos por Categoria
    st.subheader("Distribuição por Categoria")
    fig, ax = plt.subplots(figsize=(10, 5))
    resumo = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs().sort_values()
    resumo.plot(kind='barh', color='teal', ax=ax)
    st.pyplot(fig)

    # Tabela Interativa
    st.subheader("Lista de Transações")
    st.dataframe(df, use_container_width=True)
else:
    st.error("Nenhum arquivo .ofx encontrado na pasta!")