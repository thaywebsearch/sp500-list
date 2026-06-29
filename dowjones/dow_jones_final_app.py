import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Dow Jones — 30 Empresas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAPEAMENTO TICKER → DOMÍNIO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMAINS = {
    "MMM": "3m.com", "AXP": "americanexpress.com", "AMGN": "amgen.com",
    "AAPL": "apple.com", "BA": "boeing.com", "CAT": "caterpillar.com",
    "CVX": "chevron.com", "CSCO": "cisco.com", "KO": "coca-cola.com",
    "DOW": "dow.com", "GS": "goldmansachs.com", "HD": "homedepot.com",
    "HON": "honeywell.com", "IBM": "ibm.com", "INTC": "intel.com",
    "JNJ": "jnj.com", "JPM": "jpmorganchase.com", "MCD": "mcdonalds.com",
    "MRK": "merck.com", "MSFT": "microsoft.com", "NKE": "nike.com",
    "PG": "pg.com", "CRM": "salesforce.com", "TRV": "travelers.com",
    "UNH": "unitedhealthgroup.com", "VZ": "verizon.com", "V": "visa.com",
    "WBA": "walgreens.com", "DIS": "disney.com", "NVDA": "nvidia.com",
}

def get_logo_url(ticker: str) -> str:
    domain = DOMAINS.get(ticker.strip().upper(), "")
    if domain:
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
    return ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS INJECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&display=swap');

:root {
  --bg:      #000008;
  --surface: #0d0d1a;
  --border:  #1a1a35;
  --accent:  #00b4ff;
  --accent2: #bf00ff;
  --green:   #00e676;
  --text:    #c8d8ff;
  --muted:   #4a4a7a;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 2rem !important;
  max-width: 1100px !important;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Rajdhani', sans-serif;
  color: var(--text);
}

/* ESTILO CIRCULAR PARA LOGOS (200x200 logic) */
[data-testid="stDataFrame"] img {
    border-radius: 50% !important;
    border: 2px solid var(--accent) !important;
    padding: 2px;
    background: white;
    object-fit: cover;
}

.dj-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(2rem, 5vw, 3.5rem);
  letter-spacing: .08em;
  background: linear-gradient(135deg, var(--accent) 0%, #fff 45%, var(--accent2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}
.dj-sub {
  font-size: 13px; font-weight: 300;
  color: var(--muted); letter-spacing: .08em;
  margin-bottom: 20px;
}
.dj-divider {
  width: 100%; height: 1px;
  background: linear-gradient(to right, transparent, var(--accent), var(--accent2), transparent);
  margin-bottom: 28px; opacity: .35;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.markdown('<h1 class="dj-title">Dow Jones Industrial Average</h1><p class="dj-sub">30 empresas · Logos via Google API · Filtro por nome, ticker e setor</p><div class="dj-divider"></div>', unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────
@st.cache_data
def load_dj():
    try:
        df = pd.read_csv("dowjones/dowjones-table.csv")
    except:
        df = pd.DataFrame([["AAPL","Apple","Information Technology"]], columns=["ticker","company","sector"])
    df["logo"] = df["ticker"].apply(get_logo_url)
    return df

df = load_dj()

# ── Table ─────────────────────────────────────────────────────────
st.data_editor(
    df,
    column_config={
        "logo": st.column_config.ImageColumn(
            "Logo",
            width="small",
            help="Google Favicon API",
        ),
        "ticker": st.column_config.TextColumn("Ticker", width="small"),
        "company": st.column_config.TextColumn("Empresa", width="large"),
        "sector": st.column_config.TextColumn("Setor", width="medium"),
    },
    column_order=["logo", "ticker", "company", "sector"],
    hide_index=True,
    use_container_width=True,
    disabled=True,
)
