import pandas as pd
import re
import pathlib

# Centralização das categorias para facilitar manutenção
CATEGORIES_MAP = {
    '🚗 Mobilidade': ['POSTO', 'PETROZATT', 'RODOVIAS', 'UBER', '99APP'],
    '🍎 Alimentação': ['IFOOD', 'MCDONALD', 'ZAMP', 'OXXO', 'SUPERMERCADO'],
    '📺 Assinaturas': ['GOOGLE', 'HBO', 'RAPIDCLOUD', 'NETFLIX', 'SPOTIFY'],
    '🛍️ E-commerce': ['MERCADOLIVRE', 'SHOPEE', 'AMAZON', 'KABUM'],
    '🏋️ Saúde': ['WELLHUB', 'GYMPASS', 'ACADEMIA', 'SMARTFIT', 'DROGASIL'],
    '👕 Vestuário': ['MODAS', 'OUTLET', 'PIREI', 'ZARA', 'H&M'],
    '💰 Lazer': ['STEAM', 'CINEMA', 'PLAYSTATION'],
    '🏠 EDUCACAO': ['TREINAMENT', 'ALURA'],

}

def get_category(memo: str, amount: float) -> str:
    memo_upper = memo.upper()
    for category, keywords in CATEGORIES_MAP.items():
        if any(kw in memo_upper for kw in keywords):
            return category
    return 'Pagamentos' if amount > 0 else '📦 Outros'

def parse_ofx_structured(file_path: str) -> list:
    """Lê arquivo OFX e retorna lista de dicionários padronizada."""
    path = pathlib.Path(file_path)
    if not path.exists():
        return []

    with open(path, 'r', encoding='iso-8859-1') as f:
        content = f.read()
    
    transactions = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', content, re.DOTALL)
    data = []
    
    for trn in transactions:
        date_match = re.search(r'<DTPOSTED>(\d{8})', trn)
        amt_match = re.search(r'<TRNAMT>(.*?)</TRNAMT>', trn)
        memo_match = re.search(r'<MEMO>(.*?)</MEMO>', trn)
        
        if date_match and amt_match and memo_match:
            amount = float(amt_match.group(1))
            memo = memo_match.group(1)
            date_str = date_match.group(1)
            
            data.append({
                'Data': pd.to_datetime(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"),
                'Descricao': memo,
                'Valor': amount,
                'Categoria': get_category(memo, amount)
            })
    return data