import pandas as pd
import pathlib
from utils import parse_ofx_structured

# 1. Localizar arquivos usando pathlib
current_dir = pathlib.Path('.')
files = list(current_dir.glob('*.ofx'))
all_transactions = []

# 2. Processar usando o módulo centralizado
for f in files:
    all_transactions.extend(parse_ofx_structured(str(f)))

if not all_transactions:
    print("⚠️ Nenhum dado encontrado.")
    exit()

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