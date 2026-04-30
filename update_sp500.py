import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

FILE_PATH = "sp500-table/sp500-table.md"

def fetch_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        logging.info(f"A tentar obter dados de: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        if not table:
            logging.warning("Tabela com ID 'constituents' não encontrada. A tentar fallback...")
            tables = soup.find_all('table')
            for t in tables:
                # Procura por uma tabela que contenha 'Symbol' no cabeçalho
                if t.find('th') and 'Symbol' in t.find('th').get_text():
                    table = t
                    break
        
        if not table:
            raise Exception("Não foi possível encontrar a tabela do S&P 500 na página.")

        df = pd.read_html(str(table))[0]
        logging.info(f"Dados obtidos. Total de empresas: {len(df)}")
        logging.info(f"Colunas do DataFrame: {df.columns.tolist()}") # Adicionado para depuração
        return df
    except Exception as e:
        logging.error(f"Erro ao obter dados: {e}")
        raise

def df_to_markdown(df):
    # Definir o cabeçalho padrão
    header = "| Symbol | Security | GICS Sector | GICS Sub-Industry | Yahoo Finance |\n"
    separator = "| :--- | :--- | :--- | :--- | :--- |\n"
    
    lines = [header, separator]
    
    # Mapear nomes de colunas esperados para os nomes reais no DataFrame
    column_mapping = {
        "Symbol": ["Symbol", "Symbol ", "Ticker symbol"],
        "Security": ["Security", "Security ", "Company"],
        "GICS Sector": ["GICS Sector", "GICS Sector ", "Sector"],
        "GICS Sub-Industry": ["GICS Sub-Industry", "GICS Sub-Industry ", "Sub-Industry"]
    }

    # Encontrar os nomes de colunas reais no DataFrame
    actual_columns = {}
    for expected, possible_names in column_mapping.items():
        found = False
        for name in possible_names:
            if name in df.columns:
                actual_columns[expected] = name
                found = True
                break
        if not found:
            logging.warning(f"Coluna esperada '{expected}' não encontrada. A tentar usar o índice.")
            # Fallback para índice se a coluna não for encontrada
            # Isso é menos robusto, mas pode funcionar se a ordem for consistente
            if expected == "Symbol": actual_columns[expected] = df.columns[0]
            elif expected == "Security": actual_columns[expected] = df.columns[1]
            elif expected == "GICS Sector": actual_columns[expected] = df.columns[3]
            elif expected == "GICS Sub-Industry": actual_columns[expected] = df.columns[4]

    for _, row in df.iterrows():
        symbol = str(row[actual_columns["Symbol"]])
        security = str(row[actual_columns["Security"]])
        sector = str(row[actual_columns["GICS Sector"]])
        sub = str(row[actual_columns["GICS Sub-Industry"]])
        
        yahoo_symbol = symbol.replace(".", "-")
        yahoo_url = f"https://finance.yahoo.com/quote/{yahoo_symbol}"
        
        lines.append(f"| {symbol} | {security} | {sector} | {sub} | [{yahoo_url}]({yahoo_url}) |\n")
    
    return "".join(lines)

def update_table():
    logging.info("A iniciar atualização...")
    
    # 1. Obter novos dados
    df = fetch_sp500()
    new_table_content = df_to_markdown(df)
    
    # 2. Ler o ficheiro atual (se existir)
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        logging.warning(f"Ficheiro {FILE_PATH} não encontrado. A criar novo.")
        content = "# S&P 500 — Tabela Completa\n\n"

    # 3. Lógica de substituição ultra-robusta
    # Procuramos o início da tabela (qualquer linha que comece com | Symbol)
    import re
    table_pattern = re.compile(r"\| Symbol \|.*?\n\|.*?\n(\|.*?\n)*", re.DOTALL)
    
    if table_pattern.search(content):
        logging.info("Tabela existente encontrada. A substituir...")
        # Encontrar a posição exata do cabeçalho da tabela para substituição
        match = table_pattern.search(content)
        start_index = match.start()
        end_index = match.end()
        
        # Substituir apenas o conteúdo da tabela, mantendo o que está antes e depois
        final_content = content[:start_index] + new_table_content + content[end_index:]
    else:
        logging.info("Tabela não encontrada no ficheiro. A anexar ao fim.")
        if not content.endswith("\n\n"):
            content += "\n\n"
        final_content = content + new_table_content
    
    # 4. Gravar o ficheiro
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    logging.info("Atualização concluída com sucesso!")

if __name__ == "__main__":
    try:
        update_table()
    except Exception as e:
        logging.critical(f"Falha fatal: {e}")
        import traceback
        logging.error(traceback.format_exc())
        exit(1)

     
    
      
 

     
    



  
