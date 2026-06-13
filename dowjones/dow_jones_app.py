"""
╔══════════════════════════════════════════════════════════════════╗
║         Dow Jones · Tabela com Logos                            ║
║         CSV: dowjones/dowjones-table.csv  (company·ticker·sector)║
║         Logos: Google Favicon API — gratuito, sem API key       ║
║         Técnica: ImageColumn · st.data_editor                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

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
#  Google Favicon API: https://www.google.com/s2/favicons?domain={dominio}&sz=64
#  ✔ Gratuito · ✔ Sem API key · ✔ Alta disponibilidade
#  sz=64 → ícone de 64×64px (melhor qualidade disponível)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMAINS = {
    "MMM":  "3m.com",
    "AXP":  "americanexpress.com",
    "AMGN": "amgen.com",
    "AAPL": "apple.com",
    "BA":   "boeing.com",
    "CAT":  "caterpillar.com",
    "CVX":  "chevron.com",
    "CSCO": "cisco.com",
    "KO":   "coca-cola.com",
    "DOW":  "dow.com",
    "GS":   "goldmansachs.com",
    "HD":   "homedepot.com",
    "HON":  "honeywell.com",
    "IBM":  "ibm.com",
    "INTC": "intel.com",
    "JNJ":  "jnj.com",
    "JPM":  "jpmorganchase.com",
    "MCD":  "mcdonalds.com",
    "MRK":  "merck.com",
    "MSFT": "microsoft.com",
    "NKE":  "nike.com",
    "PG":   "pg.com",
    "CRM":  "salesforce.com",
    "TRV":  "travelers.com",
    "UNH":  "unitedhealthgroup.com",
    "VZ":   "verizon.com",
    "V":    "visa.com",
    "WBA":  "walgreens.com",
    "DIS":  "disney.com",
    "NVDA": "nvidia.com",
}

def get_logo_url(ticker: str) -> str:
    """
    Devolve o URL do logo via Google Favicon API.
    Alternativa gratuita e fiável ao Clearbit (que passou a ser pago).
    sz=64 → ícone de maior qualidade disponível.
    """
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
  padding: 2rem 2rem 2rem 2rem !important;
  max-width: 1100px !important;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Rajdhani', sans-serif;
  color: var(--text);
}
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed; inset: 0;
  background: repeating-linear-gradient(
    to bottom,
    transparent, transparent 3px,
    rgba(0,180,255,.012) 3px,
    rgba(0,180,255,.012) 4px
  );
  pointer-events: none;
  z-index: 9998;
}

.dj-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(2rem, 5vw, 3.5rem);
  letter-spacing: .08em;
  background: linear-gradient(135deg, var(--accent) 0%, #fff 45%, var(--accent2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

.metric-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.metric-card {
  flex: 1; min-width: 120px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 18px; text-align: center;
  position: relative; overflow: hidden;
}
.metric-card::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(to right, var(--accent), var(--accent2));
}
.metric-value {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.9rem; color: var(--green);
  letter-spacing: .05em; line-height: 1;
}
.metric-label {
  font-size: 10px; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted); margin-top: 4px;
}

.filter-label {
  font-size: 10px; letter-spacing: .25em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 8px;
}
.stTextInput > div > div > input {
  background-color: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: 'Rajdhani', sans-serif !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 12px rgba(0,180,255,.15) !important;
}
.stSelectbox > div > div {
  background-color: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
.stTextInput label, .stSelectbox label {
  color: var(--muted) !important;
  font-size: 11px !important;
  letter-spacing: .15em !important;
  text-transform: uppercase !important;
}

.results-label {
  font-size: 11px; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 12px;
}
.results-count {
  color: var(--green);
  font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem;
}

.stDownloadButton > button {
  background: transparent !important; color: var(--accent) !important;
  border: 1px solid rgba(0,180,255,.3) !important; border-radius: 8px !important;
  font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important;
}
.stDownloadButton > button:hover { border-color: var(--accent) !important; }

.dj-footer {
  text-align: center; font-size: 10px; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted);
  padding: 28px 0 12px 0;
  border-top: 1px solid var(--border); margin-top: 36px;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<h1 class="dj-title">Dow Jones Industrial Average</h1>
<p class="dj-sub">30 empresas · Logos via Clearbit · Filtro por nome, ticker e setor</p>
<div class="dj-divider"></div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CARREGA CSV — usa o teu ficheiro original sem o modificar
#  Adiciona coluna "logo" em runtime via DOMAINS dict
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_data
def load_dj():
    df = pd.read_csv("dowjones/dowjones-table.csv")   # ← pasta/ficheiro exato no GitHub
    df["logo"] = df["ticker"].apply(get_logo_url)
    return df

df = load_dj()

# ── Métricas ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-value">{len(df)}</div>
    <div class="metric-label">Empresas</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{df["sector"].nunique()}</div>
    <div class="metric-label">Setores</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{df["logo"].astype(bool).sum()}</div>
    <div class="metric-label">Logos ativos</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Filtros ───────────────────────────────────────────────────────
st.markdown('<p class="filter-label">⬡ &nbsp; Filtros</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 2])
with col1:
    search = st.text_input("🔍 Nome ou Ticker",
                           placeholder="ex: Apple, MSFT, Nike...")
with col2:
    sector_list = ["Todos"] + sorted(df["sector"].unique().tolist())
    sector_q    = st.selectbox("🏭 Setor", sector_list)

# ── Filtra ────────────────────────────────────────────────────────
result = df.copy()

if search:
    mask = (
        result["company"].str.lower().str.contains(search.lower(), na=False) |
        result["ticker"].str.lower().str.contains(search.lower(), na=False)
    )
    result = result[mask]

if sector_q != "Todos":
    result = result[result["sector"] == sector_q]

# ── Resultados ───────────────────────────────────────────────────
st.markdown(f"""
<p class="results-label">
  ⬡ &nbsp; Resultados &nbsp;
  <span class="results-count">{len(result)}</span>
  &nbsp; empresas
</p>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TABELA COM LOGOS
#  column_order → logo aparece primeiro
#  ImageColumn  → renderiza o URL como imagem na célula
#  disabled=True → tabela read-only
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.data_editor(
    result.reset_index(drop=True),
    column_config={
        "logo": st.column_config.ImageColumn(
            "Logo",
            width="small",
            help="Clearbit Logo API",
        ),
        "ticker": st.column_config.TextColumn("Ticker", width="small"),
        "company": st.column_config.TextColumn("Empresa", width="large"),
        "sector": st.column_config.TextColumn("Setor", width="medium"),
    },
    column_order=["logo", "ticker", "company", "sector"],
    hide_index=True,
    use_container_width=True,
    height=500,
    disabled=True,
)

# ── Download ──────────────────────────────────────────────────────
st.download_button(
    label="⬇️  Exportar CSV",
    data=result[["ticker","company","sector"]].to_csv(index=False).encode("utf-8"),
    file_name="dow_jones_export.csv",
    mime="text/csv",
)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("""
<div class="dj-footer">
  ⬡ &nbsp; Logos: Google Favicon API &nbsp;·&nbsp;
  Dados: Dow Jones Industrial Average &nbsp; ⬡
</div>
""", unsafe_allow_html=True)
