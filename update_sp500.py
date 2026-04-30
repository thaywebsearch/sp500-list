import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import os
import re
import time

# Configuração de logging profissional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

FILE_PATH = "sp500-table/sp500-table.md"

def fetch_sp500_with_retry(retries=3, backoff=2):
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    # User-Agent altamente específico conforme a política da Wikipédia
    # Inclui o nome do script e um contacto genérico (pode ser o link do repo)
    headers = {
        'User-Agent': 'SP500Bot/1.0 (https://github.com/thaywebsearch/sp500-list; mailto:admin@example.com) python-requests/2.31.0',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for attempt in range(retries):
        try:
            logging.info(f"Tentativa {attempt + 1}: Acedendo à Wikipédia...")
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 403:
                logging.error("Erro 403: Acesso negado pela Wikipédia. Verifique o User-Agent ou bloqueio de IP.")
                if attempt < retries - 1:
                    time.sleep(backoff * (attempt + 1))
                    continue
                response.raise_for_status()
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"id": "constituents"})
            
            if not table:
                logging.warning("Tabela 'constituents' não encontrada por ID. A procurar por classe 'wikitable'...")
                tables = soup.find_all('table', class_='wikitable')
                for t in tables:
                    if 'Symbol' in t.get_text():
                        table = t
                        break
            
            if not table:
                raise ValueError("Não foi possível localizar a tabela de constituintes na página.")

            # Extração robusta com Pandas
            df = pd.read_html(str(table))[0]
            
            # Limpeza básica de nomes de colunas (remover espaços e caracteres estranhos)
            df.columns = [str(c).strip() for c in df.columns]
            
            logging.info(f"Sucesso! {len(df)} empresas encontradas.")
            return df

        except Exception as e:
            logging.error(f"Erro na tentativa {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                raise

def generate_markdown_table(df):
    # Identificar colunas dinamicamente para evitar erros de nomes alterados
    col_map = {
        'Symbol': next((c for c in df.columns if 'Symbol' in c or 'Ticker' in c), None),
        'Security': next((c for c in df.columns if 'Security' in c or 'Company' in c), None),
        'Sector': next((c for c in df.columns if 'Sector' in c), None),
        'SubIndustry': next((c for c in df.columns if 'Sub-Industry' in c), None)
    }
    
    if not all(col_map.values()):
        logging.error(f"Colunas detetadas: {df.columns.tolist()}")
        raise KeyError(f"Não foi possível mapear todas as colunas necessárias. Mapeamento: {col_map}")

    header = "| Symbol | Security | GICS Sector | GICS Sub-Industry | Yahoo Finance |\n"
    separator = "| :--- | :--- | :--- | :--- | :--- |\n"
    rows = []
    
    for _, row in df.iterrows():
        symbol = str(row[col_map['Symbol']]).replace('\n', '').strip()
        security = str(row[col_map['Security']]).replace('\n', '').strip()
        sector = str(row[col_map['Sector']]).replace('\n', '').strip()
        sub = str(row[col_map['SubIndustry']]).replace('\n', '').strip()
        
        # Yahoo Finance usa '-' em vez de '.' para classes de ações (ex: BRK.B -> BRK-B)
        yahoo_symbol = symbol.replace('.', '-')
        yahoo_url = f"https://finance.yahoo.com/quote/{yahoo_symbol}"
        
        rows.append(f"| {symbol} | {security} | {sector} | {sub} | [Link]({yahoo_url}) |")
    
    return header + separator + "\n".join(rows) + "\n"

def main():
    try:
        # 1. Obter dados
        df = fetch_sp500_with_retry()
        new_table = generate_markdown_table(df)
        
        # 2. Ler ficheiro atual
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# S&P 500 List\n\n"
            os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

        # 3. Substituição inteligente
        # Procura por uma tabela Markdown existente ou anexa ao fim
        table_regex = re.compile(r"\| Symbol \| Security \|.*?\n\| :--- \|.*?\n(\|.*?\n)*", re.DOTALL)
        
        if table_regex.search(content):
            logging.info("Substituindo tabela existente no Markdown.")
            updated_content = table_regex.sub(new_table, content)
        else:
            logging.info("Tabela não encontrada. Anexando ao final do ficheiro.")
            updated_content = content.rstrip() + "\n\n" + new_table
            
        # 4. Salvar
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
        logging.info("Processo concluído com sucesso.")

    except Exception as e:
        logging.critical(f"Falha no script: {e}")
        import traceback
        logging.error(traceback.format_exc())
        exit(1)

if __name__ == "__main__":
    main()

    

   
  
   
     

     
    
      
 

     
    



  
