# 📖 Explicação Técnica do Sistema

Este documento descreve o funcionamento interno das ferramentas deste repositório para facilitar a manutenção e evolução do sistema.

## 1. Lógica de Extração (OFX Parsing)
A maioria dos scripts (`analise.py`, `dashboard_final.py`, etc.) utiliza a função `parse_ofx`. Em vez de bibliotecas externas complexas, usamos **Expressões Regulares (Regex)** para processar o conteúdo dos arquivos OFX:

- **Regex utilizada**: `<STMTTRN>(.*?)</STMTTRN>` para capturar blocos de transação.
- **Campos extraídos**: Valor (`<TRNAMT>`), Descrição (`<MEMO>`) e Data (`<DTPOSTED>`).
- **Encoding**: Utilizamos `iso-8859-1` para garantir a leitura correta de caracteres especiais comuns em extratos bancários brasileiros.

## 2. Motor de Categorização Inteligente
O sistema utiliza um motor de busca por palavras-chave para classificar os gastos automaticamente. 

```python
if any(k in memo for k in ['POSTO', 'PETROZATT']): cat = '🚗 Mobilidade'
```

Os scripts verificam se sub-strings específicas existem na descrição da transação (`MEMO`). Nos dashboards mais recentes, implementamos uma "Análise de Resíduos" para identificar quais itens ainda estão caindo na categoria "Outros", permitindo o refinamento contínuo das regras.

## 3. Web Scraping (Mercado Livre)
Os arquivos `extrator_ml.py` e `extrator_ml_v2.py` utilizam **Selenium** para resolver um problema comum: as faturas de cartão mostram apenas "MercadoLivre", sem dizer o que foi comprado.

- O script automatiza a navegação até a lista de compras.
- Ele extrai o nome do produto e o valor.
- O `dashboard_premium.py` realiza um **Merge (Join)** entre o CSV do Mercado Livre e os dados do OFX usando o valor como chave, substituindo nomes genéricos pelos nomes reais dos produtos.

## 4. Visualização de Dados (Dashboards)
Utilizamos o **Streamlit** em conjunto com **Plotly** para criar a interface:

- **Pandas**: Gerencia toda a manipulação de tabelas (DataFrames), filtros de data e agrupamentos (Groupby).
- **Plotly Express**: Gera os gráficos de Pareto (Barras), Share de Carteira (Pizza/Donut) e Evolução Temporal (Linhas/Área).
- **Caching**: Os dados são processados em tempo de execução ao carregar os arquivos `.ofx` locais.

## 5. Fluxo de Dados
1. **Input**: Arquivos `.ofx` (Extratos) e execução do extrator de ML.
2. **Processamento**: Scripts Python limpam e categorizam os dados.
3. **Output**: 
   - Arquivos `minhas_financas.csv/xlsx` para uso manual.
   - Dashboards interativos via navegador (`localhost`).

## 6. Segurança
O projeto foi desenhado com o princípio de **Zero Cloud**. Nenhum dado financeiro sai da sua máquina. O arquivo `.gitignore` garante que mesmo que você suba o código para o GitHub, seus dados pessoais permanecerão protegidos localmente.

---
_Documentação técnica para suporte ao desenvolvedor._
