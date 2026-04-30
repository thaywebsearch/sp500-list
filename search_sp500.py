import pandas as pd

FILE_PATH = "sp500-table/sp500-table.csv"

def load_data():
    return pd.read_csv(FILE_PATH)

def search_company(df, query):
    query = query.lower()
    return df[df["Security"].str.lower().str.contains(query)]

def search_ticker(df, ticker):
    ticker = ticker.upper()
    return df[df["Symbol"] == ticker]

def search_sector(df, sector):
    sector = sector.lower()
    return df[df["GICS Sector"].str.lower().str.contains(sector)]

def sort_alphabetically(df):
    return df.sort_values(by="Security")

if __name__ == "__main__":
    df = load_data()

    print("\n=== S&P 500 Search Tool ===")
    print("1. Procurar empresa por nome")
    print("2. Procurar por ticker")
    print("3. Procurar por setor")
    print("4. Ordenar por ordem alfabética\n")

    option = input("Escolhe uma opção: ")

    if option == "1":
        q = input("Nome da empresa: ")
        print(search_company(df, q))

    elif option == "2":
        t = input("Ticker: ")
        print(search_ticker(df, t))

    elif option == "3":
        s = input("Setor: ")
        print(search_sector(df, s))

    elif option == "4":
        print(sort_alphabetically(df))

    else:
        print("Opção inválida.")
