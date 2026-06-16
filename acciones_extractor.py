import os
import time
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import concurrent.futures

from rate_limiter import limitador_finnhub
from indicadores import analizar_serie

# ── API KEY ──────────────────────────────────────────────────
# Se lee primero de st.secrets (Streamlit Cloud / .streamlit/secrets.toml).
# Si no existe (ej. corriendo un script suelto fuera de Streamlit, como el
# backtest desde la terminal), cae a una variable de entorno. Nunca se
# deja la clave escrita en texto plano en el código.
def _obtener_api_key() -> str:
    try:
        return st.secrets["FINNHUB_API_KEY"]
    except Exception:
        return os.environ.get("FINNHUB_API_KEY", "")

API_KEY = _obtener_api_key()

BMV = ["AMXL.MX","FEMSAUBD.MX","BIMBOA.MX","WALMEX.MX","GMEXICOB.MX",
       "TLEVICPO.MX","AC.MX","GCARSOA1.MX","ALSEA.MX","KOFUBL.MX"]
NYSE = ["AAPL","NVDA","MSFT","GOOGL","AMZN","TSLA","META","JPM","V","UNH"]
PENNY = ["SNDL","CLOV","GRAB","NKLA","HIMS","OPEN","SOFI","WKHS","EXPR","BIRD"]
HIGH_BETA = ["RIOT","MARA","COIN","PLTR","HOOD","RKLB","IONQ","SMCI","MSTR","AFRM"]
CRYPTO = ["BINANCE:BTCUSDT","BINANCE:ETHUSDT","BINANCE:SOLUSDT",
          "BINANCE:BNBUSDT","BINANCE:DOGEUSDT","BINANCE:XRPUSDT",
          "BINANCE:ADAUSDT","BINANCE:AVAXUSDT","BINANCE:DOTUSDT","BINANCE:MATICUSDT"]

# Configuración de sesión robusta
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))


def _buscar(data: dict, *claves, default=None):
    """Busca la primera clave presente entre varias variantes posibles.
    Finnhub no siempre usa el mismo nombre de campo para todos los
    mercados/cuentas, así que probamos varios alias conocidos."""
    for clave in claves:
        valor = data.get(clave)
        if valor is not None:
            return valor
    return default


def _metricas_default() -> dict:
    return {"beta": 1.0, "pe": 0, "pb": None, "mktcap": 0, "roe": None,
            "debt_equity": None, "rev_growth": None, "div_yield": None}


@st.cache_data(ttl=21600, show_spinner=False)  # 6 horas: los fundamentales no cambian intradía
def obtener_metricas(symbol: str) -> dict:
    try:
        limitador_finnhub.esperar()
        r = session.get(
            "https://finnhub.io/api/v1/stock/metric",
            params={"symbol": symbol, "metric": "all", "token": API_KEY},
            timeout=8
        )
        if r.status_code == 429:
            return _metricas_default()

        r.raise_for_status()
        data = r.json().get("metric", {}) or {}
        return {
            "beta": _buscar(data, "beta", default=1.0),
            "pe": _buscar(data, "peExclExtraTTM", "peNormalizedAnnual", "peTTM", default=0),
            "pb": _buscar(data, "pbAnnual", "pbQuarterly", default=None),
            "mktcap": _buscar(data, "marketCapitalization", default=0),
            "roe": _buscar(data, "roeTTM", "roeRfy", "roe5Y", default=None),
            "debt_equity": _buscar(data, "totalDebt/totalEquityQuarterly",
                                    "totalDebt/totalEquityAnnual", default=None),
            "rev_growth": _buscar(data, "revenueGrowthTTMYoy", "revenueGrowthQuarterlyYoy",
                                   "revenueGrowth5Y", default=None),
            "div_yield": _buscar(data, "dividendYieldIndicatedAnnual", default=None),
        }
    except requests.exceptions.RequestException:
        return _metricas_default()


@st.cache_data(ttl=21600, show_spinner=False)  # 6 horas, y sirve tanto al score como al gráfico y al backtest
def obtener_historial(symbol: str, dias: int = 400) -> pd.DataFrame:
    try:
        limitador_finnhub.esperar()
        ahora = int(time.time())
        inicio = ahora - dias * 24 * 3600
        r = session.get(
            "https://finnhub.io/api/v1/stock/candle",
            params={
                "symbol"    : symbol,
                "resolution": "D",
                "from"      : inicio,
                "to"        : ahora,
                "token"     : API_KEY,
            },
            timeout=10
        )
        if r.status_code == 429:
            return pd.DataFrame()

        r.raise_for_status()
        data = r.json()
        if data.get("s") != "ok":
            return pd.DataFrame()
        df = pd.DataFrame({
            "Date" : pd.to_datetime(data["t"], unit="s"),
            "Close": data["c"],
        })
        return df.sort_values("Date").reset_index(drop=True)
    except requests.exceptions.RequestException:
        return pd.DataFrame()


def obtener_quote(symbol: str) -> dict:
    try:
        limitador_finnhub.esperar()
        r = session.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": API_KEY},
            timeout=10
        )
        if r.status_code == 429:
            return {"error": "rate_limit"}

        r.raise_for_status()
        data = r.json()
        precio   = data.get("c", 0)
        anterior = data.get("pc", precio)
        cambio   = ((precio - anterior) / anterior * 100) if anterior else 0

        if precio == 0:
            return {}

        metricas = obtener_metricas(symbol)
        hist = obtener_historial(symbol)
        indicadores = analizar_serie(hist["Close"]) if not hist.empty else \
            {"RSI": None, "SMA20": None, "SMA50": None, "MACD Hist": None}

        return {
            "Ticker"              : symbol.replace(".MX",""),
            "Nombre"              : symbol.replace(".MX",""),
            "Precio"              : round(precio, 2),
            "Cambio %"            : round(cambio, 2),
            "Volumen"             : data.get("v", 0),
            "52w Alto"            : data.get("h", 0),
            "52w Bajo"            : data.get("l", 0),
            "Beta"                : round(metricas["beta"], 2) if metricas["beta"] else 1.0,
            "P/E"                 : round(metricas["pe"], 2) if metricas["pe"] else None,
            "P/B"                 : round(metricas["pb"], 2) if metricas["pb"] else None,
            "ROE"                 : round(metricas["roe"], 2) if metricas["roe"] else None,
            "Deuda/Capital"       : round(metricas["debt_equity"], 2) if metricas["debt_equity"] else None,
            "Crecimiento Ingresos": round(metricas["rev_growth"], 2) if metricas["rev_growth"] else None,
            "Dividend Yield"      : round(metricas["div_yield"], 2) if metricas["div_yield"] else None,
            "Mkt Cap"             : metricas["mktcap"],
            "Recomendacion"       : "—",
            **indicadores,
        }
    except requests.exceptions.RequestException:
        return {}


def obtener_crypto_quote(symbol: str) -> dict:
    try:
        limitador_finnhub.esperar()
        r = session.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": API_KEY},
            timeout=10
        )
        if r.status_code == 429:
            return {"error": "rate_limit"}

        r.raise_for_status()
        data  = r.json()
        precio = data.get("c", 0)
        anterior = data.get("pc", precio)
        cambio   = ((precio - anterior) / anterior * 100) if anterior else 0
        nombre   = symbol.replace("BINANCE:","").replace("USDT","")
        if precio == 0:
            return {}

        hist = obtener_historial(symbol)
        indicadores = analizar_serie(hist["Close"]) if not hist.empty else \
            {"RSI": None, "SMA20": None, "SMA50": None, "MACD Hist": None}

        return {
            "Ticker"              : nombre,
            "Nombre"              : nombre,
            "Precio"              : round(precio, 4),
            "Cambio %"            : round(cambio, 2),
            "Volumen"             : data.get("v", 0),
            "52w Alto"            : data.get("h", 0),
            "52w Bajo"            : data.get("l", 0),
            "Beta"                : 1.0,
            "P/E"                 : None,
            "P/B"                 : None,
            "ROE"                 : None,
            "Deuda/Capital"       : None,
            "Crecimiento Ingresos": None,
            "Dividend Yield"      : None,
            "Mkt Cap"             : None,
            "Recomendacion"       : "—",
            **indicadores,
        }
    except requests.exceptions.RequestException:
        return {}


def cargar_grupo(tickers: list, nombre: str, es_crypto: bool = False) -> pd.DataFrame:
    filas = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        if es_crypto:
            resultados = executor.map(obtener_crypto_quote, tickers)
        else:
            resultados = executor.map(obtener_quote, tickers)

        for dato in resultados:
            if dato:
                if dato.get("error") == "rate_limit":
                    continue
                dato["Grupo"] = nombre
                filas.append(dato)

    return pd.DataFrame(filas) if filas else pd.DataFrame()


def obtener_todos() -> dict:
    return {
        "BMV"      : cargar_grupo(BMV,       "🇲🇽 BMV"),
        "NYSE"     : cargar_grupo(NYSE,      "🇺🇸 NYSE/NASDAQ"),
        "Penny"    : cargar_grupo(PENNY,     "💰 Penny Stocks"),
        "High Beta": cargar_grupo(HIGH_BETA, "⚡ Beta Elevada"),
        "Crypto"   : cargar_grupo(CRYPTO,    "🪙 Cripto", es_crypto=True),
    }
