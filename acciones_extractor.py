import yfinance as yf
import pandas as pd

BMV = [
    "AMXL.MX","FEMSAUBD.MX","BIMBOA.MX","WALMEX.MX","GMEXICOB.MX",
    "TLEVICPO.MX","AC.MX","GCARSOA1.MX","ALSEA.MX","KOFUBL.MX"
]
NYSE = [
    "AAPL","NVDA","MSFT","GOOGL","AMZN",
    "TSLA","META","JPM","V","UNH"
]
PENNY = [
    "SNDL","CLOV","GRAB","NKLA","WKHS",
    "EXPR","HIMS","OPEN","SOFI","BIRD"
]
HIGH_BETA = [
    "RIOT","MARA","COIN","PLTR","HOOD",
    "RKLB","IONQ","SMCI","MSTR","AFRM"
]
CRYPTO = [
    "BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD",
    "ADA-USD","DOGE-USD","AVAX-USD","DOT-USD","MATIC-USD"
]

def obtener_datos(tickers, nombre_grupo):
    filas = []
    for ticker in tickers:
        try:
            t    = yf.Ticker(ticker)
            info = t.info
            precio   = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            anterior = info.get("previousClose", precio)
            cambio   = ((precio - anterior) / anterior * 100) if anterior else 0
            filas.append({
                "Ticker"       : ticker.replace(".MX",""),
                "Nombre"       : info.get("shortName", ticker)[:25],
                "Grupo"        : nombre_grupo,
                "Precio"       : round(precio, 2),
                "Cambio %"     : round(cambio, 2),
                "Volumen"      : info.get("volume", 0),
                "Beta"         : info.get("beta", None),
                "P/E"          : info.get("trailingPE", None),
                "Mkt Cap"      : info.get("marketCap", None),
                "52w Alto"     : info.get("fiftyTwoWeekHigh", None),
                "52w Bajo"     : info.get("fiftyTwoWeekLow", None),
                "Recomendacion": info.get("recommendationKey", "—"),
            })
        except Exception:
            pass
    return pd.DataFrame(filas)

def obtener_todos():
    return {
        "BMV"       : obtener_datos(BMV,       "🇲🇽 BMV"),
        "NYSE"      : obtener_datos(NYSE,      "🇺🇸 NYSE/NASDAQ"),
        "Penny"     : obtener_datos(PENNY,     "💰 Penny Stocks"),
        "High Beta" : obtener_datos(HIGH_BETA, "⚡ Beta Elevada"),
        "Crypto"    : obtener_datos(CRYPTO,    "🪙 Cripto"),
    }
