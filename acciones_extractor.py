import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import concurrent.futures
import time
import streamlit as st

API_KEY = st.secrets["FINNHUB_API_KEY"]

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

def obtener_metricas(symbol: str) -> dict:
    try:
        r = session.get(
            "https://finnhub.io/api/v1/stock/metric",
            params={"symbol": symbol, "metric": "all", "token": API_KEY},
            timeout=5
        )
        if r.status_code == 429:
            return {"beta": 1.0, "pe": 0, "mktcap": 0}
        
        r.raise_for_status()
        data = r.json().get("metric", {})
        return {
            "beta": data.get("beta", 1.0),
            "pe": data.get("peExclExtraTTM", 0),
            "mktcap": data.get("marketCapitalization", 0)
        }
    except requests.exceptions.RequestException:
        return {"beta": 1.0, "pe": 0, "mktcap": 0}

def obtener_quote(symbol: str) -> dict:
    try:
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

        return {
            "Ticker"       : symbol.replace(".MX",""),
            "Nombre"       : symbol.replace(".MX",""),
            "Precio"       : round(precio, 2),
            "Cambio %"     : round(cambio, 2),
            "Volumen"      : data.get("v", 0), 
            "52w Alto"     : data.get("h", 0),
            "52w Bajo"     : data.get("l", 0),
            "Beta"         : round(metricas["beta"], 2) if metricas["beta"] else 1.0,
            "P/E"          : round(metricas["pe"], 2) if metricas["pe"] else None,
            "Mkt Cap"      : metricas["mktcap"],
            "Recomendacion": "—",
        }
    except requests.exceptions.RequestException:
        return {}

def obtener_crypto_quote(symbol: str) -> dict:
    try:
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
        return {
            "Ticker"       : nombre,
            "Nombre"       : nombre,
            "Precio"       : round(precio, 4),
            "Cambio %"     : round(cambio, 2),
            "Volumen"      : data.get("v", 0),
            "52w Alto"     : data.get("h", 0),
            "52w Bajo"     : data.get("l", 0),
            "Beta"         : 1.0,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
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
                
    time.sleep(1)
    return pd.DataFrame(filas) if filas else pd.DataFrame()

def obtener_todos() -> dict:
    return {
        "BMV"      : cargar_grupo(BMV,       "🇲🇽 BMV"),
        "NYSE"     : cargar_grupo(NYSE,      "🇺🇸 NYSE/NASDAQ"),
        "Penny"    : cargar_grupo(PENNY,     "💰 Penny Stocks"),
        "High Beta": cargar_grupo(HIGH_BETA, "⚡ Beta Elevada"),
        "Crypto"   : cargar_grupo(CRYPTO,    "🪙 Cripto", es_crypto=True),
    }
