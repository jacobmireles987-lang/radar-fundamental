# acciones_extractor.py
import requests
import pandas as pd

API_KEY = "d8k6lmpr01qjgd6ruqs0d8k6lmpr01qjgd6ruqsg"

BMV = ["AMXL.MX","FEMSAUBD.MX","BIMBOA.MX","WALMEX.MX","GMEXICOB.MX",
       "TLEVICPO.MX","AC.MX","GCARSOA1.MX","ALSEA.MX","KOFUBL.MX"]
NYSE = ["AAPL","NVDA","MSFT","GOOGL","AMZN","TSLA","META","JPM","V","UNH"]
PENNY = ["SNDL","CLOV","GRAB","NKLA","HIMS","OPEN","SOFI","WKHS","EXPR","BIRD"]
HIGH_BETA = ["RIOT","MARA","COIN","PLTR","HOOD","RKLB","IONQ","SMCI","MSTR","AFRM"]
CRYPTO = ["BINANCE:BTCUSDT","BINANCE:ETHUSDT","BINANCE:SOLUSDT",
          "BINANCE:BNBUSDT","BINANCE:DOGEUSDT","BINANCE:XRPUSDT",
          "BINANCE:ADAUSDT","BINANCE:AVAXUSDT","BINANCE:DOTUSDT","BINANCE:MATICUSDT"]

def obtener_quote(symbol: str) -> dict:
    try:
        r = requests.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": API_KEY},
            timeout=10
        )
        data = r.json()
        precio   = data.get("c", 0)
        anterior = data.get("pc", precio)
        cambio   = ((precio - anterior) / anterior * 100) if anterior else 0
        high     = data.get("h", 0)
        low      = data.get("l", 0)

        if precio == 0:
            return {}

        return {
            "Ticker"       : symbol.replace(".MX",""),
            "Nombre"       : symbol.replace(".MX",""),
            "Precio"       : round(precio, 2),
            "Cambio %"     : round(cambio, 2),
            "Volumen"      : 0,
            "52w Alto"     : high,
            "52w Bajo"     : low,
            "Beta"         : None,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
        }
    except Exception:
        return {}

def obtener_perfil(symbol: str) -> dict:
    try:
        r = requests.get(
            "https://finnhub.io/api/v1/stock/profile2",
            params={"symbol": symbol, "token": API_KEY},
            timeout=10
        )
        return r.json()
    except Exception:
        return {}

def obtener_crypto_quote(symbol: str) -> dict:
    try:
        r = requests.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": API_KEY},
            timeout=10
        )
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
            "Volumen"      : 0,
            "52w Alto"     : data.get("h", 0),
            "52w Bajo"     : data.get("l", 0),
            "Beta"         : None,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
        }
    except Exception:
        return {}

def cargar_grupo(tickers: list, nombre: str, es_crypto: bool = False) -> pd.DataFrame:
    filas = []
    for t in tickers:
        dato = obtener_crypto_quote(t) if es_crypto else obtener_quote(t)
        if dato:
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
