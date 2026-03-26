from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def scroll_to_bottom(driver):
    """Rola a página até o fim para carregar todos os itens (Infinite Scroll)."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Rola até o fim da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Aguarda o carregamento de novos itens
        # Calcula nova altura e compara com a anterior
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def process_purchase_elements(elementos):
    """Extrai dados de uma lista de WebElements do Selenium."""
    compras = []
    for i in elementos:
        try:
            texto_completo = i.text.split('\n')
            # Lógica: O título geralmente é a primeira ou segunda linha
            # O valor é a linha que contém "R$"
            valor = next((s for s in texto_completo if "R$" in s), "0")
            titulo = texto_completo[0] if len(texto_completo) > 0 else "Desconhecido"
            data = next((s for s in texto_completo if "/" in s), "Sem data")

            compras.append({
                'Produto': titulo,
                'Data_Compra': data,
                'Valor_ML': valor
            })
        except:
            continue
    return compras

if __name__ == "__main__":
    # Configuração de Perfil Persistente (User Data Directory)
    # Isso salva cookies, cache e sessões em uma pasta local, evitando logins repetidos.
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chrome_data")
    # Opcional: chrome_options.add_argument("--profile-directory=Default")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://myaccount.mercadolivre.com.br/my_purchases/list")

    # Seletor genérico para os blocos de compra
    xpath_compras = "//div[contains(@class, 'purchase-card') or contains(@class, 'sh-item')]"

    try:
        # Espera automática: aguarda até 10 segundos para que ao menos um card apareça
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_compras))
        )
    except:
        # Se estourar o tempo, verificamos se caiu na tela de login
        if "login" in driver.current_url or not driver.find_elements(By.XPATH, xpath_compras):
            input("👉 Sessão não encontrada ou expirada. Faça login MANUALMENTE e pressione ENTER aqui...")

    # Executa a rolagem automática para carregar o histórico completo
    print("⏳ Rolando a página para carregar todas as compras...")
    scroll_to_bottom(driver)

    # Captura os elementos após a garantia de que a página carregou
    elementos = driver.find_elements(By.XPATH, xpath_compras)

    print(f"Encontrados {len(elementos)} blocos de possíveis compras. Analisando...")
    compras_ml = process_purchase_elements(elementos)

    if compras_ml:
        df_ml = pd.DataFrame(compras_ml)
        df_ml = df_ml.drop_duplicates().dropna()
        df_ml.to_csv('compras_detalhadas_ml.csv', index=False, encoding='utf-8-sig')
        print(f"✅ Sucesso! {len(df_ml)} itens guardados.")
    else:
        print("❌ Nenhum item encontrado.")

    driver.quit()