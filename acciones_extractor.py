import requests
import pandas as pd
import time

API_KEY = "NTTE78R1NO78U4OV"

BMV       = ["AMXL.MX","FEMSAUBD.MX","BIMBOA.MX","WALMEX.MX","GMEXICOB.MX"]
NYSE      = ["AAPL","NVDA","MSFT","TSLA","META"]
PENNY     = ["SNDL","CLOV","GRAB","HIMS","SOFI"]
HIGH_BETA = ["RIOT","MARA","COIN","PLTR","HOOD"]
CRYPTO    = ["BTC","ETH","SOL","BNB","DOGE"]

def obtener_quote(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol"  : symbol,
        "apikey"  : API_KEY,
    }
    try:
        r    = requests.get(url, params=params, timeout=10)
        data = r.json().get("Global Quote", {})
        if not data:
            return {}
        precio = float(data.get("05. price", 0))
        cambio = float(data.get("10. change percent", "0%").replace("%",""))
        return {
            "Ticker"       : symbol.replace(".MX",""),
            "Nombre"       : symbol.replace(".MX",""),
            "Precio"       : round(precio, 2),
            "Cambio %"     : round(cambio, 2),
            "Volumen"      : int(data.get("06. volume", 0)),
            "52w Alto"     : float(data.get("03. high", 0)),
            "52w Bajo"     : float(data.get("04. low", 0)),
            "Beta"         : None,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
        }
    except Exception:
        return {}

def obtener_crypto(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function"     : "CURRENCY_EXCHANGE_RATE",
        "from_currency": symbol,
        "to_currency"  : "USD",
        "apikey"       : API_KEY,
    }
    try:
        r    = requests.get(url, params=params, timeout=10)
        data = r.json().get("Realtime Currency Exchange Rate", {})
        if not data:
            return {}
        precio = float(data.get("5. Exchange Rate", 0))
        return {
            "Ticker"       : symbol,
            "Nombre"       : data.get("1. From_Currency Name", symbol)[:20],
            "Precio"       : round(precio, 4),
            "Cambio %"     : 0.0,
            "Volumen"      : 0,
            "52w Alto"     : 0,
            "52w Bajo"     : 0,
            "Beta"         : None,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
        }
    except Exception:
        return {}

def cargar_grupo(tickers, nombre, es_crypto=False):
    filas = []
    for t in tickers:
        dato = obtener_crypto(t) if es_crypto else obtener_quote(t)
        if dato:
            dato["Grupo"] = nombre
            filas.append(dato)
        time.sleep(0.3)
    return pd.DataFrame(filas) if filas else pd.DataFrame()

def obtener_todos():
    return {
        "BMV"      : cargar_grupo(BMV,       "🇲🇽 BMV"),
        "NYSE"     : cargar_grupo(NYSE,      "🇺🇸 NYSE/NASDAQ"),
        "Penny"    : cargar_grupo(PENNY,     "💰 Penny Stocks"),
        "High Beta": cargar_grupo(HIGH_BETA, "⚡ Beta Elevada"),
        "Crypto"   : cargar_grupo(CRYPTO,    "🪙 Cripto", es_crypto=True),
    }
