"""
╔══════════════════════════════════════════════════════════════════╗
║         S&P 500 Search Tool · app.py                            ║
║         Branding: Logo animado + Search Tool integrados         ║
║         Técnica: CSS Injection + Base64 Image + Streamlit       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="S&P 500 Search Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Logo Base64 (inline — sem dependência externa) ────────────────
def img_to_base64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")

def get_mime_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {"png": "image/png", "jpg": "image/jpeg",
            "jpeg": "image/jpeg", "webp": "image/webp",
            "gif": "image/gif", "svg": "image/svg+xml"}.get(ext.strip("."), "image/png")

logo_b64  = img_to_base64("logo.png")
logo_mime = get_mime_type("logo.png")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS GLOBAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&display=swap');

:root {
  --bg:       #000008;
  --surface:  #0d0d1a;
  --border:   #1a1a35;
  --accent:   #00b4ff;
  --accent2:  #bf00ff;
  --accent3:  #6e00ff;
  --green:    #00e676;
  --text:     #c8d8ff;
  --muted:    #4a4a7a;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 0 2rem 2rem 2rem !important;
  max-width: 1200px !important;
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

/* ── HEADER ── */
.sp-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 24px;
  padding: 28px 0 24px 0;
  position: relative;
}

.sp-header::before {
  content: "";
  position: absolute;
  width: 600px; height: 300px;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(ellipse,
    rgba(110,0,255,.10) 0%,
    rgba(0,180,255,.06) 40%,
    transparent 70%
  );
  pointer-events: none;
  animation: ambient-pulse 7s ease-in-out infinite;
}

@keyframes ambient-pulse {
  0%,100% { opacity:.6; transform: translate(-50%,-50%) scale(1);    }
  50%      { opacity:1;  transform: translate(-50%,-50%) scale(1.15); }
}

/* ── logo ring ── */
.sp-logo-wrap {
  position: relative;
  width: 80px; height: 80px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.sp-logo-wrap::before {
  content: "";
  position: absolute; inset: -10px;
  border-radius: 50%;
  border: 1px solid rgba(0,180,255,.2);
  border-top-color: rgba(0,180,255,.85);
  border-right-color: rgba(191,0,255,.5);
  animation: spin 10s linear infinite;
}

.sp-logo-wrap::after {
  content: "";
  position: absolute; inset: -18px;
  border-radius: 50%;
  border: 1px dashed rgba(191,0,255,.15);
  border-bottom-color: rgba(191,0,255,.55);
  animation: spin 16s linear infinite reverse;
}

@keyframes spin { to { transform: rotate(360deg); } }

.sp-orbit {
  position: absolute; inset: -10px; border-radius: 50%;
  animation: spin 10s linear infinite; pointer-events: none;
}
.sp-orbit-dot {
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent), 0 0 18px var(--accent);
}
.sp-orbit2 {
  position: absolute; inset: -18px; border-radius: 50%;
  animation: spin 16s linear infinite reverse; pointer-events: none;
}
.sp-orbit-dot2 {
  position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
  width: 4px; height: 4px; border-radius: 50%;
  background: var(--accent2);
  box-shadow: 0 0 6px var(--accent2), 0 0 14px var(--accent2);
}

.sp-logo {
  width: 72px; height: 72px;
  object-fit: cover;
  border-radius: 50%;
  animation: logo-float 6s ease-in-out infinite,
             logo-glow  4s ease-in-out infinite;
}

@keyframes logo-float {
  0%,100% { transform: translateY(0px)  scale(1);    }
  30%      { transform: translateY(-9px) scale(1.02); }
  60%      { transform: translateY(-5px) scale(.99);  }
}

@keyframes logo-glow {
  0%,100% {
    filter: drop-shadow(0 0 16px rgba(0,180,255,.5))
            drop-shadow(0 0 5px  rgba(191,0,255,.3));
  }
  50% {
    filter: drop-shadow(0 0 36px rgba(0,180,255,.9))
            drop-shadow(0 0 16px rgba(191,0,255,.65))
            drop-shadow(0 0 50px rgba(110,0,255,.4));
  }
}

/* ── title block ── */
.sp-title-block { display: flex; flex-direction: column; gap: 4px; }

.sp-eyebrow {
  font-size: 10px; font-weight: 300;
  letter-spacing: .4em; text-transform: uppercase;
  color: var(--muted);
  animation: fade-up .8s ease both;
}

.sp-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  letter-spacing: .06em; line-height: 1;
  background: linear-gradient(135deg, var(--accent) 0%, #fff 45%, var(--accent2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fade-up .9s ease .1s both;
}

.sp-subtitle {
  font-size: 13px; font-weight: 300;
  color: var(--muted); letter-spacing: .06em;
  animation: fade-up 1s ease .2s both;
}

.sp-pills {
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-top: 8px;
  animation: fade-up 1s ease .3s both;
}

.sp-pill {
  padding: 3px 12px; border-radius: 4px;
  font-size: 9px; letter-spacing: .16em;
  text-transform: uppercase; font-weight: 600;
  border: 1px solid rgba(0,180,255,.2);
  color: rgba(0,180,255,.6);
  background: rgba(0,180,255,.04);
}

.sp-divider {
  width: 100%; height: 1px;
  background: linear-gradient(to right, transparent, var(--accent), var(--accent2), transparent);
  margin: 0 0 32px 0; opacity: .35;
}

/* ── METRICS ── */
.metric-row { display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }

.metric-card {
  flex: 1; min-width: 130px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px; text-align: center;
  position: relative; overflow: hidden;
}

.metric-card::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(to right, var(--accent), var(--accent2));
}

.metric-value {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem; color: var(--green);
  letter-spacing: .05em; line-height: 1;
}

.metric-label {
  font-size: 10px; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted); margin-top: 4px;
}

/* ── SEARCH ── */
.search-label {
  font-size: 10px; letter-spacing: .25em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 20px;
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
.stTextInput label, .stSelectbox label, .stCheckbox label {
  color: var(--muted) !important;
  font-size: 11px !important;
  letter-spacing: .15em !important;
  text-transform: uppercase !important;
}
.stButton > button {
  background: linear-gradient(135deg, var(--accent3), var(--accent)) !important;
  color: #fff !important; font-family: 'Rajdhani', sans-serif !important;
  font-weight: 700 !important; letter-spacing: .1em !important;
  border: none !important; border-radius: 8px !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; }

.stDataFrame { border: 1px solid var(--border) !important; border-radius: 10px !important; }

.results-label {
  font-size: 11px; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 12px;
}
.results-count {
  color: var(--green);
  font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem;
}

.stDownloadButton > button {
  background: transparent !important; color: var(--accent) !important;
  border: 1px solid rgba(0,180,255,.3) !important; border-radius: 8px !important;
  font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important;
}
.stDownloadButton > button:hover { border-color: var(--accent) !important; }

.sp-footer {
  text-align: center; font-size: 10px; letter-spacing: .2em;
  text-transform: uppercase; color: var(--muted);
  padding: 32px 0 16px 0;
  border-top: 1px solid var(--border); margin-top: 40px;
}

hr { border-color: var(--border) !important; }

@keyframes fade-up {
  from { opacity:0; transform: translateY(20px); }
  to   { opacity:1; transform: translateY(0);    }
}
</style>
"""

HEADER = f"""
<div class="sp-header">
  <div class="sp-logo-wrap">
    <div class="sp-orbit"><div class="sp-orbit-dot"></div></div>
    <div class="sp-orbit2"><div class="sp-orbit-dot2"></div></div>
    <img class="sp-logo"
         src="data:{logo_mime};base64,{logo_b64}"
         alt="Logo" />
  </div>
  <div class="sp-title-block">
    <span class="sp-eyebrow">⬡ &nbsp; mercado · ativo &nbsp; ⬡</span>
    <h1 class="sp-title">S&amp;P 500 Search Tool</h1>
    <p class="sp-subtitle">Pesquisa inteligente de empresas do índice S&amp;P 500</p>
    <div class="sp-pills">
      <span class="sp-pill">503 Empresas</span>
      <span class="sp-pill">11 Setores</span>
      <span class="sp-pill">Live Data</span>
      <span class="sp-pill">CSV Export</span>
    </div>
  </div>
</div>
<div class="sp-divider"></div>
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"

@st.cache_data(ttl=3600)
def load_data():
    try:
        return pd.read_csv(URL)
    except Exception:
        return pd.read_csv("sp500-table/sp500-table.csv")

def search_company(df, q):
    return df[df["Security"].str.lower().str.contains(q.lower(), na=False)]

def search_ticker(df, t):
    return df[df["Symbol"] == t.upper()]

def search_sector(df, s):
    return df if s == "All" else df[df["GICS Sector"] == s]

def sort_alpha(df):
    return df.sort_values(by="Security")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RENDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(CSS,    unsafe_allow_html=True)
st.markdown(HEADER, unsafe_allow_html=True)

with st.spinner("A carregar dados do S&P 500..."):
    df = load_data()

# Metrics
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-value">{len(df)}</div>
    <div class="metric-label">Empresas</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{df["GICS Sector"].nunique()}</div>
    <div class="metric-label">Setores</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{df["Symbol"].nunique()}</div>
    <div class="metric-label">Tickers</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">AUTO</div>
    <div class="metric-label">Atualização</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Search
st.markdown('<p class="search-label">⬡ &nbsp; Filtros de pesquisa</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    name_q = st.text_input("🔍 Nome da empresa", placeholder="ex: Apple, Microsoft, Tesla...")
with col2:
    ticker_q = st.text_input("🏷️ Ticker", placeholder="ex: AAPL")
with col3:
    sector_list = ["All"] + sorted(df["GICS Sector"].dropna().unique().tolist())
    sector_q = st.selectbox("🏭 Setor GICS", sector_list)

col4, _ = st.columns([1, 5])
with col4:
    do_sort = st.checkbox("Ordenar A→Z")

# Filter
result = df.copy()
if name_q:     result = search_company(result, name_q)
if ticker_q:   result = search_ticker(result, ticker_q)
if sector_q != "All": result = search_sector(result, sector_q)
if do_sort:    result = sort_alpha(result)

# Results
st.markdown(f"""
<p class="results-label">
  ⬡ &nbsp; Resultados &nbsp;
  <span class="results-count">{len(result)}</span>
  &nbsp; empresas encontradas
</p>
""", unsafe_allow_html=True)

if len(result) == 0:
    st.warning("Nenhuma empresa encontrada. Tenta outro critério.")
else:
    st.dataframe(result.reset_index(drop=True), use_container_width=True, height=480)
    st.download_button(
        label="⬇️  Exportar resultados CSV",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="sp500_results.csv",
        mime="text/csv"
    )

# Footer
st.markdown("""
<div class="sp-footer">
  ⬡ &nbsp; Dados: GitHub datasets/s-and-p-500-companies &nbsp;·&nbsp;
  Atualizado automaticamente via GitHub Actions &nbsp; ⬡
</div>
""", unsafe_allow_html=True)
