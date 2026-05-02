import pandas as pd
import streamlit as st

# --- Config ---
st.set_page_config(
    page_title="S&P 500 Search",
    page_icon="📈",
    layout="wide"
)

# --- CSS dark theme ---
st.markdown("""
<style>
    .stApp { background-color: #0D1117; color: #E6EDF3; }
    .stTextInput > div > div > input {
        background-color: #161B22;
        color: #E6EDF3;
        border: 1px solid #00E676;
        border-radius: 8px;
    }
    .stSelectbox > div > div {
        background-color: #161B22;
        color: #E6EDF3;
        border: 1px solid #30363D;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #21262D;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #00E676; }
    .metric-label { font-size: 0.85rem; color: #8B949E; }
    .stDataFrame { background-color: #161B22; }
    div[data-testid="stMetricValue"] { color: #00E676; }
    .stButton > button {
        background-color: #00E676;
        color: #0D1117;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }
    h1, h2, h3 { color: #E6EDF3; }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv(URL)
    except:
        # fallback to local file
        df = pd.read_csv("sp500-table/sp500-table.csv")
    return df

# --- Search functions ---
def search_company(df, query):
    return df[df["Security"].str.lower().str.contains(query.lower(), na=False)]

def search_ticker(df, ticker):
    return df[df["Symbol"] == ticker.upper()]

def search_sector(df, sector):
    if sector == "All":
        return df
    return df[df["GICS Sector"] == sector]

def sort_alphabetically(df):
    return df.sort_values(by="Security")

# --- Header ---
st.markdown("## 📈 S&P 500 Search Tool")
st.markdown("Pesquisa empresas do índice S&P 500 por nome, ticker ou setor.")
st.divider()

# --- Load ---
with st.spinner("A carregar dados..."):
    df = load_data()

# --- Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Empresas", len(df))
with col2:
    st.metric("Setores", df["GICS Sector"].nunique())
with col3:
    st.metric("Última atualização", "Auto (GitHub)")

st.divider()

# --- Search UI ---
col_a, col_b, col_c = st.columns([2, 1, 2])

with col_a:
    name_query = st.text_input("🔍 Pesquisar por nome", placeholder="ex: Apple, Microsoft...")

with col_b:
    ticker_query = st.text_input("🏷️ Pesquisar por ticker", placeholder="ex: AAPL")

with col_c:
    sectors = ["All"] + sorted(df["GICS Sector"].dropna().unique().tolist())
    sector_query = st.selectbox("🏭 Filtrar por setor", sectors)

col_d, col_e = st.columns([1, 4])
with col_d:
    sort_alpha = st.checkbox("Ordenar A-Z")

# --- Filter logic ---
result = df.copy()

if name_query:
    result = search_company(result, name_query)

if ticker_query:
    result = search_ticker(result, ticker_query)

if sector_query != "All":
    result = search_sector(result, sector_query)

if sort_alpha:
    result = sort_alphabetically(result)

# --- Results ---
st.divider()
st.markdown(f"### Resultados: **{len(result)}** empresas encontradas")

if len(result) == 0:
    st.warning("Nenhuma empresa encontrada. Tenta outro critério de pesquisa.")
else:
    st.dataframe(
        result.reset_index(drop=True),
        use_container_width=True,
        height=500
    )

    # Download button
    csv = result.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download resultados CSV",
        data=csv,
        file_name="sp500_search_results.csv",
        mime="text/csv"
    )

# --- Footer ---
st.divider()
st.markdown("<p style='text-align:center; color:#8B949E; font-size:0.8rem;'>Dados: GitHub datasets/s-and-p-500-companies • Atualizado automaticamente</p>", unsafe_allow_html=True)
