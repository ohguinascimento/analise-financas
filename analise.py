import pandas as pd
import re
import os

# 1. Função para ler OFX e transformar em dicionário
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
            memo = memo_match.group(1)
            
            # Categorização Inteligente
            m = memo.upper()
            if any(kw in m for kw in ['POSTO', 'PETROZATT', 'RODOVIAS']): cat = 'Combustível'
            elif any(kw in m for kw in ['GOOGLE', 'HBO', 'RAPIDCLOUD', 'REGISTRO.BR']): cat = 'Assinaturas'
            elif any(kw in m for kw in ['HOTEL', 'Morumby', 'MOTEIS']): cat = 'Hospedagem'
            elif any(kw in m for kw in ['MODAS', 'OUTLET', 'PIREI', 'GBMMODAS']): cat = 'Vestuário'
            elif any(kw in m for kw in ['MERCADOLIVRE', 'SHOPEE', 'AMAZON', 'KABUM']): cat = 'Marketplace'
            elif amount > 0: cat = 'Pagamentos'
            else: cat = 'Outros'
            
            data.append({'Data': date, 'Descricao': memo, 'Valor': amount, 'Categoria': cat})
    return data

# 2. Listar ficheiros e processar
files = [f for f in os.listdir('.') if f.endswith('.ofx')]
all_transactions = []

for f in files:
    all_transactions.extend(parse_ofx(f))

# 3. Criar o DataFrame
df = pd.DataFrame(all_transactions)
df = df.sort_values('Data')

# 4. Salvar resultados localmente
df.to_csv('minhas_financas.csv', index=False, encoding='utf-8-sig')
df.to_excel('minhas_financas.xlsx', index=False)

print("✅ Base de dados criada com sucesso em CSV e Excel!")

# 5. Exibir resumo no console
resumo = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().abs()
print("\nResumo de Gastos por Categoria:")
print(resumo)