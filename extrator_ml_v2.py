from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://myaccount.mercadolivre.com.br/my_purchases/list")

input("👉 Faça login, ESPERE A PÁGINA CARREGAR TOTALMENTE e pressione ENTER aqui...")

compras_ml = []

# Procura por todos os blocos que pareçam uma compra
# Usamos um seletor genérico de 'article' ou 'div' de alto nível
elementos = driver.find_elements(By.XPATH, "//div[contains(@class, 'purchase-card') or contains(@class, 'sh-item')]")

print(f"Encontrados {len(elementos)} blocos de possíveis compras. Analisando...")

for i in elementos:
    try:
        # Busca qualquer texto que comece com R$ dentro do bloco
        texto_completo = i.text.split('\n')
        
        # Lógica: O título geralmente é a primeira ou segunda linha
        # O valor é a linha que contém "R$"
        valor = next((s for s in texto_completo if "R$" in s), "0")
        titulo = texto_completo[0] if len(texto_completo) > 0 else "Desconhecido"
        data = next((s for s in texto_completo if "/" in s), "Sem data")

        compras_ml.append({
            'Produto': titulo,
            'Data_Compra': data,
            'Valor_ML': valor
        })
    except:
        continue

if compras_ml:
    df_ml = pd.DataFrame(compras_ml)
    # Limpeza extra: remover duplicados e linhas vazias
    df_ml = df_ml.drop_duplicates().dropna()
    df_ml.to_csv('compras_detalhadas_ml.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Sucesso! {len(df_ml)} itens guardados em 'compras_detalhadas_ml.csv'.")
else:
    print("❌ Ainda não foi possível encontrar itens. Tente rolar a página até o fim antes de dar ENTER.")

driver.quit()