import pandas as pd

# URL estável do DataHub.io (S&P 500 constituents)
URL = "https://datahub.io/core/s-and-p-500-companies/r/data/constituents.csv"

# Caminho onde o ficheiro será guardado no repositório
CSV_PATH = "sp500-table/sp500-table.csv"
MD_PATH = "sp500-table/sp500-table.md"

def fetch_sp500():
    """Descarrega a lista do S&P 500 a partir do DataHub.io."""
    df = pd.read_csv(URL)
    return df

def df_to_markdown(df):
    """Converte DataFrame para Markdown."""
    return df.to_markdown(index=False)

def save_files(df):
    """Guarda CSV e Markdown no repositório."""
    df.to_csv(CSV_PATH, index=False)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(df_to_markdown(df))

if __name__ == "__main__":
    df = fetch_sp500()
    save_files(df)
    print("S&P 500 atualizado com sucesso!")

    
  
       
       
   
    


     
            

    

   
  
   
     

     
    
      
 

     
    



  
