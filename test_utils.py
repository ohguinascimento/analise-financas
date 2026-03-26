import pytest
import pandas as pd
from utils import get_category, parse_ofx_structured
import tempfile
import os

def test_get_category_known_keywords():
    """Garante que palavras-chave conhecidas retornam as categorias corretas."""
    assert get_category("UBER TRIP", -25.0) == "🚗 Mobilidade"
    assert get_category("IFOOD *LANCHES", -50.0) == "🍎 Alimentação"
    assert get_category("NETFLIX.COM", -39.9) == "📺 Assinaturas"
    assert get_category("AMAZON MARKETPLACE", -100.0) == "🛍️ E-commerce"

def test_get_category_default_cases():
    """Valida o comportamento para transações desconhecidas ou entradas de dinheiro."""
    assert get_category("TRANSFERENCIA RECEBIDA", 500.0) == "Pagamentos"
    assert get_category("COMPRA DESCONHECIDA", -10.0) == "📦 Outros"

def test_parse_ofx_structured_invalid_path():
    """Garante que o parser lida corretamente com arquivos inexistentes."""
    assert parse_ofx_structured("arquivo_que_nao_existe.ofx") == []

def test_parse_ofx_logic_with_temp_file():
    """Testa a extração de dados de um conteúdo OFX real usando um arquivo temporário."""
    ofx_content = """
    <STMTTRN>
        <TRNAMT>-150.00</TRNAMT>
        <DTPOSTED>20231027120000</DTPOSTED>
        <MEMO>POSTO IPIRANGA</MEMO>
    </STMTTRN>
    <STMTTRN>
        <TRNAMT>-45.90</TRNAMT>
        <DTPOSTED>20231028120000</DTPOSTED>
        <MEMO>NETFLIX</MEMO>
    </STMTTRN>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False, encoding='iso-8859-1') as tmp:
        tmp.write(ofx_content)
        tmp_path = tmp.name

    try:
        results = parse_ofx_structured(tmp_path)
        assert len(results) == 2
        assert results[0]['Valor'] == -150.0
        assert results[0]['Categoria'] == "🚗 Mobilidade"
        assert results[1]['Descricao'] == "NETFLIX"
        assert isinstance(results[0]['Data'], pd.Timestamp)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)