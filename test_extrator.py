import pytest
from unittest.mock import MagicMock
from extrator_ml_v2 import process_purchase_elements

def test_process_purchase_elements_mocked():
    """Testa a lógica de extração simulando elementos do Selenium."""
    
    # Criamos o primeiro Mock de elemento (Compra válida)
    mock_el1 = MagicMock()
    mock_el1.text = "Fone de Ouvido Bluetooth\nR$ 150,00\nEntregue 10/Jan"
    
    # Criamos o segundo Mock de elemento (Compra com estrutura diferente)
    mock_el2 = MagicMock()
    mock_el2.text = "Camiseta Algodão\n15/Jan\nR$ 59,90"
    
    # Lista de elementos que o Selenium retornaria
    mock_elementos = [mock_el1, mock_el2]
    
    # Executamos a função passando os Mocks
    resultado = process_purchase_elements(mock_elementos)
    
    # Asserções
    assert len(resultado) == 2
    assert resultado[0]['Produto'] == "Fone de Ouvido Bluetooth"
    assert resultado[0]['Valor_ML'] == "R$ 150,00"
    
    assert resultado[1]['Produto'] == "Camiseta Algodão"
    assert resultado[1]['Valor_ML'] == "R$ 59,90"
    assert "15/Jan" in resultado[1]['Data_Compra']