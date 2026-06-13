"""
╔══════════════════════════════════════════════════════════════════╗
║         S&P 500 Search Tool · app.py                            ║
║         Branding: Logo animado + Search Tool integrados         ║
║         Técnica: CSS Injection + Base64 Image + Streamlit       ║
║         Estrutura 2: Price column via yfinance                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE CONFIG — tem de ser a primeira chamada Streamlit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="S&P 500 Dashboard — Lista Completa",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.header("S&P 500 — Lista Completa de Empresas")
st.text("Explore todas as 500 empresas do índice S&P 500, "
        "com dados de mercado, sector e capitalização.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOGO BASE64
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
#  PREÇOS VIA YFINANCE
#  - ttl=3600 → cache de 1 hora (não sobrecarrega a API)
#  - batch de 100 tickers por chamada → muito mais rápido
#  - fallback "N/A" se o ticker falhar
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_market_data(tickers: tuple):
    """
    Recebe uma tuple de tickers e devolve três dicts:
      - prices     : {ticker: preço em USD}
      - market_caps: {ticker: market cap formatado em B/T}
      - pe_ratios  : {ticker: P/E Ratio formatado}

    Estratégia:
      - Price      → yf.download() em batch de 100 (rápido)
      - Market Cap → yf.Ticker().fast_info (leve, sem histórico)
      - P/E Ratio  → yf.Ticker().info["trailingPE"]
                     (trailing P/E — baseado nos últimos 12 meses reais)

    O que é o P/E Ratio:
      Preço da ação ÷ Lucro por ação (EPS)
      → P/E alto  = mercado paga prémio (ex: crescimento esperado)
      → P/E baixo = empresa barata ou em dificuldade
      → N/A       = empresa com lucro negativo ou dado indisponível
    """
    import yfinance as yf

    prices      = {}
    market_caps = {}
    pe_ratios   = {}
    w52_highs   = {}
    w52_lows    = {}
    div_yields  = {}
    betas       = {}
    batch_size  = 100
    ticker_list = list(tickers)

    # ── PRICE — batch download ────────────────────────────────────
    for i in range(0, len(ticker_list), batch_size):
        batch = ticker_list[i : i + batch_size]
        try:
            data = yf.download(
                tickers     = batch,
                period      = "1d",
                interval    = "1d",
                progress    = False,
                auto_adjust = True,
            )
            if hasattr(data.columns, "get_level_values") and \
               "Close" in data.columns.get_level_values(0):
                close = data["Close"]
            else:
                close = data

            for ticker in batch:
                try:
                    val = close[ticker].dropna().iloc[-1] if ticker in close.columns else None
                    prices[ticker] = round(float(val), 2) if val is not None else "N/A"
                except Exception:
                    prices[ticker] = "N/A"
        except Exception:
            for ticker in batch:
                prices[ticker] = "N/A"

    # ── MARKET CAP + P/E RATIO — info por ticker ─────────────────
    #    P/E Ratio só disponível em .info (não em fast_info)
    #    Market Cap usa fast_info (mais rápido)
    for ticker in ticker_list:
        try:
            t    = yf.Ticker(ticker)
            info = t.info
            cap  = t.fast_info.market_cap

            # Market Cap
            if cap is None:
                market_caps[ticker] = "N/A"
            elif cap >= 1_000_000_000_000:
                market_caps[ticker] = f"${cap / 1_000_000_000_000:.2f}T"
            elif cap >= 1_000_000_000:
                market_caps[ticker] = f"${cap / 1_000_000_000:.2f}B"
            else:
                market_caps[ticker] = f"${cap / 1_000_000:.0f}M"

            # P/E Ratio — trailing 12 meses
            pe = info.get("trailingPE")
            if pe is None or pe != pe:      # None ou NaN
                pe_ratios[ticker] = "N/A"
            elif pe < 0:                    # empresa com prejuízo
                pe_ratios[ticker] = "neg."
            else:
                pe_ratios[ticker] = f"{pe:.1f}x"

            # 52W High — máximo dos últimos 52 semanas
            high = t.fast_info.year_high
            if high is None or high != high:
                w52_highs[ticker] = "N/A"
            else:
                price_now = prices.get(ticker)
                if isinstance(price_now, float) and high > 0:
                    pct = ((price_now - high) / high) * 100
                    w52_highs[ticker] = f"${high:.2f} ({pct:+.1f}%)"
                else:
                    w52_highs[ticker] = f"${high:.2f}"

            # 52W Low — mínimo dos últimos 52 semanas
            low = t.fast_info.year_low
            if low is None or low != low:
                w52_lows[ticker] = "N/A"
            else:
                price_now = prices.get(ticker)
                if isinstance(price_now, float) and low > 0:
                    pct = ((price_now - low) / low) * 100
                    w52_lows[ticker] = f"${low:.2f} (+{pct:.1f}%)"
                else:
                    w52_lows[ticker] = f"${low:.2f}"

            # Dividend Yield — rendimento do dividendo anual
            # dividendYield → valor decimal (ex: 0.015 = 1.5%)
            # N/A → empresa que não paga dividendo
            dy = info.get("dividendYield")
            if dy is None or dy != dy or dy == 0:
                div_yields[ticker] = "—"        # não paga dividendo
            else:
                div_yields[ticker] = f"{dy * 100:.2f}%"

            # Beta — volatilidade relativa ao S&P 500
            # β < 1  → menos volátil (ex: utilities, consumer staples)
            # β = 1  → move-se igual ao mercado
            # β > 1  → mais volátil (ex: tech, growth)
            # β < 0  → move-se inversamente ao mercado
            beta = info.get("beta")
            if beta is None or beta != beta:
                betas[ticker] = "N/A"
            else:
                betas[ticker] = f"{beta:.2f}"

        except Exception:
            market_caps[ticker] = "N/A"
            pe_ratios[ticker]   = "N/A"
            w52_highs[ticker]   = "N/A"
            w52_lows[ticker]    = "N/A"
            div_yields[ticker]  = "N/A"
            betas[ticker]       = "N/A"

    return prices, market_caps, pe_ratios, w52_highs, w52_lows, div_yields, betas


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

/* ── PRICE BADGE na tabela ── */
.price-tag {
  display: inline-block;
  background: rgba(0,230,118,.08);
  color: #00e676;
  border: 1px solid rgba(0,230,118,.25);
  border-radius: 4px;
  padding: 1px 8px;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 13px;
  letter-spacing: .05em;
}

.price-na {
  color: var(--muted);
  font-size: 12px;
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

/* ── INFO PRICE ── */
.price-info {
  font-size: 11px; letter-spacing: .12em;
  color: var(--muted); margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
}
.price-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--green);
  display: inline-block;
  animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
  0%,100% { opacity:1; }
  50%      { opacity:.3; }
}

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
      <span class="sp-pill">Live Price</span>
      <span class="sp-pill">CSV Export</span>
    </div>
  </div>
</div>
<div class="sp-divider"></div>
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATA — carrega o CSV do S&P 500
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

# ── 1. Carrega o CSV ──────────────────────────────────────────────
with st.spinner("A carregar dados do S&P 500..."):
    df = load_data()

# ── 2. Carrega todos os dados de mercado via yfinance ─────────────
with st.spinner("A obter cotações, market caps, P/E, 52W, Dividend Yield, Beta... ⏳  (cache de 1h)"):
    tickers_tuple                                                          = tuple(df["Symbol"].tolist())
    prices, market_caps, pe_ratios, w52_highs, w52_lows, div_yields, betas = fetch_market_data(tickers_tuple)

# ── 3. Adiciona colunas ao DataFrame ──────────────────────────────
df["Price (USD)"]     = df["Symbol"].map(prices)
df["Market Cap"]      = df["Symbol"].map(market_caps)
df["P/E Ratio"]       = df["Symbol"].map(pe_ratios)
df["52W High"]        = df["Symbol"].map(w52_highs)
df["52W Low"]         = df["Symbol"].map(w52_lows)
df["Dividend Yield"]  = df["Symbol"].map(div_yields)
df["Beta"]            = df["Symbol"].map(betas)

# ── Metrics ───────────────────────────────────────────────────────
valid_prices  = [v for v in prices.values() if v != "N/A"]
valid_caps    = [v for v in market_caps.values() if v != "N/A"]
valid_pe      = [v for v in pe_ratios.values() if v not in ("N/A", "neg.")]
avg_price     = round(sum(valid_prices) / len(valid_prices), 2) if valid_prices else 0
avg_pe        = round(sum(float(v.replace("x","")) for v in valid_pe) / len(valid_pe), 1) if valid_pe else 0

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
    <div class="metric-value">{len(valid_prices)}</div>
    <div class="metric-label">Preços obtidos</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{len(valid_caps)}</div>
    <div class="metric-label">Market Caps</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">${avg_price}</div>
    <div class="metric-label">Preço médio</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{avg_pe}x</div>
    <div class="metric-label">P/E médio S&amp;P</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────────────
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

# ── Filter ────────────────────────────────────────────────────────
result = df.copy()
if name_q:             result = search_company(result, name_q)
if ticker_q:           result = search_ticker(result, ticker_q)
if sector_q != "All":  result = search_sector(result, sector_q)
if do_sort:            result = sort_alpha(result)

# ── Results ───────────────────────────────────────────────────────
st.markdown(f"""
<p class="results-label">
  ⬡ &nbsp; Resultados &nbsp;
  <span class="results-count">{len(result)}</span>
  &nbsp; empresas encontradas
</p>
""", unsafe_allow_html=True)

# Indicador de frescura dos dados
st.markdown("""
<p class="price-info">
  <span class="price-dot"></span>
  Cotações · Market Cap · P/E · 52W High/Low · Dividend Yield · Beta · Actualização automática a cada hora
</p>
""", unsafe_allow_html=True)

if len(result) == 0:
    st.warning("Nenhuma empresa encontrada. Tenta outro critério.")
else:
    # Reordena colunas — Price, Market Cap, P/E e 52W High logo após Symbol e Security
    cols = ["Symbol", "Security", "Price (USD)", "Market Cap", "P/E Ratio",
            "52W High", "52W Low", "Dividend Yield", "Beta",
            "GICS Sector", "GICS Sub-Industry", "Headquarters Location", "Date added", "Founded"]
    cols_available = [c for c in cols if c in result.columns]
    result_display = result[cols_available].reset_index(drop=True)

    st.dataframe(result_display, use_container_width=True, height=480)

    st.download_button(
        label="⬇️  Exportar resultados CSV",
        data=result_display.to_csv(index=False).encode("utf-8"),
        file_name="sp500_results.csv",
        mime="text/csv"
    )

# ── Footer ────────────────────────────────────────────────────────
st.markdown("""
<div class="sp-footer">
  ⬡ &nbsp; Dados: GitHub datasets/s-and-p-500-companies &nbsp;·&nbsp;
  Cotações: Yahoo Finance via yfinance &nbsp;·&nbsp;
  Actualizado automaticamente via GitHub Actions &nbsp; ⬡
</div>
""", unsafe_allow_html=True)
