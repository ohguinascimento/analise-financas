from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time

# 1. Configurar o Navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 2. Acessar a página
url = "https://myaccount.mercadolivre.com.br/my_purchases/list"
driver.get(url)

input("👉 Faça o login no navegador e depois pressione ENTER aqui no terminal...")

# 3. Função para extrair dados da página atual
compras_ml = []

def extrair_pagina():
    # O ML costuma usar estas tags para os títulos das compras
    # Tentamos múltiplos seletores para garantir a captura
    itens = driver.find_elements(By.CSS_SELECTOR, ".sh-item__item-container") # Novo seletor comum
    
    if not itens:
        # Seletor alternativo caso a estrutura mude
        itens = driver.find_elements(By.XPATH, "//div[contains(@class, 'card')]")

    for item in itens:
        try:
            # Tenta pegar o título por seletores comuns de texto
            titulo = item.find_element(By.TAG_NAME, "h2").text 
            valor = item.find_element(By.CLASS_NAME, "money-amount__fraction").text
            data = item.find_element(By.CLASS_NAME, "purchase-date").text # Ajuste conforme necessário
            
            compras_ml.append({
                'Produto': titulo,
                'Data_Compra': data,
                'Valor_ML': valor
            })
        except:
            continue

# Executa a extração
print("Extraindo dados...")
extrair_pagina()

# 4. Salvar para o seu BI
df_ml = pd.DataFrame(compras_ml)
df_ml.to_csv('compras_detalhadas_ml.csv', index=False, encoding='utf-8-sig')

print(f"✅ Sucesso! {len(df_ml)} itens extraídos.")
driver.quit()