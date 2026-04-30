import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILE_PATH = "sp500-table/sp500-table.md"

def fetch_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        logging.info(f"A tentar obter dados de: {url}")
        html = requests.get(url, headers=headers, timeout=10).text # Adicionado timeout e headers
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        if not table:
            raise Exception("Tabela de constituintes do S&P 500 não encontrada na página da Wikipédia.")
        df = pd.read_html(str(table))[0]
        logging.info("Dados do S&P 500 obtidos com sucesso.")
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de rede ao obter dados da Wikipédia: {e}")
        raise
    except Exception as e:
        logging.error(f"Erro ao analisar dados da Wikipédia: {e}")
        raise

def df_to_markdown(df):
    lines = []
    for _, row in df.iterrows():
        symbol = row["Symbol"]
        security = row["Security"]
        sector = row["GICS Sector"]
        sub = row["GICS Sub-Industry"]
        # Adiciona tratamento para símbolos que podem ter caracteres especiais no URL do Yahoo Finance
        yahoo_symbol = symbol.replace('.', '-') # Ex: BRK.B -> BRK-B
        yahoo = f"https://finance.yahoo.com/quote/{yahoo_symbol}"
        lines.append(f"| {symbol} | {security} | {sector} | {sub} | [{yahoo}]({yahoo}) |")
    return "\n".join(lines)

def update_table():
    logging.info("A iniciar a atualização da tabela S&P 500.")
    try:
        df = fetch_sp500()
        new_table_markdown = df_to_markdown(df)

        with open(FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        start_table_marker_str = "| Symbol | Security | GICS Sector | GICS Sub-Industry | Yahoo Finance |"
        start_table_marker_index = content.find(start_table_marker_str)

        if start_table_marker_index == -1:
            raise Exception(f"Marcador de início da tabela '{start_table_marker_str}' não encontrado no ficheiro '{FILE_PATH}'.")

        # Encontra o fim da tabela atual, procurando por duas novas linhas após o cabeçalho da tabela
        # ou o fim do ficheiro se não houver mais conteúdo.
        end_table_header_index = start_table_marker_index + len(start_table_marker_str)
        end_table_content_index = content.find("\n\n", end_table_header_index)

        if end_table_content_index == -1:
            # Se não encontrar duas novas linhas, assume que a tabela vai até o fim do ficheiro
            end_table_content_index = len(content)
        else:
            # Adiciona 2 para incluir as duas novas linhas que marcam o fim da tabela
            end_table_content_index += 2

        # Preserva o conteúdo antes da tabela e adiciona a nova tabela
        # A nova tabela inclui o cabeçalho, então substituímos a partir do início do cabeçalho antigo.
        final_content = content[:start_table_marker_index] + start_table_marker_str + "\n" + new_table_markdown + content[end_table_content_index:]

        with open(FILE_PATH, "w", encoding="utf-8") as f:
            f.write(final_content)
        logging.info(f"Ficheiro '{FILE_PATH}' atualizado com sucesso.")

    except FileNotFoundError:
        logging.error(f"Ficheiro '{FILE_PATH}' não encontrado. Certifique-se de que o caminho está correto e o ficheiro existe.")
        raise
    except Exception as e:
        logging.error(f"Erro ao atualizar a tabela: {e}")
        raise

if __name__ == "__main__":
    try:
        update_table()
    except Exception as e:
        logging.critical(f"O script falhou: {e}")
        exit(1)

    

     
    



  
