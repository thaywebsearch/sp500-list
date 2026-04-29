import requests
import pandas as pd
from bs4 import BeautifulSoup

FILE_PATH = "sp500-table/sp500-table.md"

def fetch_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    df = pd.read_html(str(table))[0]
    return df

def df_to_markdown(df):
    lines = []
    for _, row in df.iterrows():
        symbol = row["Symbol"]
        security = row["Security"]
        sector = row["GICS Sector"]
        sub = row["GICS Sub-Industry"]
        yahoo = f"https://finance.yahoo.com/quote/{symbol}"
        lines.append(f"| {symbol} | {security} | {sector} | {sub} | {yahoo} |")
    return "\n".join(lines)

def update_table():
    df = fetch_sp500()
    new_table = df_to_markdown(df)

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start = content.find("| Symbol")
    if start == -1:
        raise Exception("Tabela não encontrada no ficheiro.")

    header_end = content.find("\n", start)
    final_content = content[:header_end] + "\n" + new_table

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(final_content)

if __name__ == "__main__":
    update_table()

