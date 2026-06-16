"""
Backtest de la componente TÉCNICA de la estrategia.

Limitación importante y honesta: Finnhub (plan gratuito) solo da el valor
ACTUAL de los fundamentales (P/E, ROE, deuda, etc.), no su valor histórico
día por día. Por lo tanto no es posible backtestear correctamente la
componente fundamental — aplicar el P/E de HOY a una fecha de hace 8 meses
sería un backtest inválido (look-ahead bias). Por eso este módulo evalúa
únicamente la señal técnica, que sí se puede calcular de forma honesta en
cualquier punto del pasado a partir del histórico de precios.

Regla de señal usada en el backtest:
    RSI < 35  (zona de sobreventa, de corto plazo)
    Y precio > SMA150  (la tendencia de fondo, de largo plazo, sigue intacta)

Nota de diseño: probamos primero exigir también MACD histograma > 0 en el
mismo día (como tercera condición), y por separado usar SMA50 en vez de
SMA150 como filtro de tendencia. Ambas variantes casi nunca disparaban
señal: una caída suficiente para hundir el RSI(14) a zona de sobreventa
casi siempre arrastra también al SMA50 hacia abajo (son ventanas de tiempo
demasiado parecidas), y el histograma de MACD reacciona con varios días de
rezago respecto al mínimo del RSI, por lo que exigir ambos el mismo día es
demasiado estricto. Por eso el filtro de tendencia usa una media más lenta
(SMA150, casi insensible a una caída de pocos días) y el MACD se deja
fuera de esta regla — sigue siendo parte del Score Técnico en vivo, pero
ahí pesa de forma gradual (vía z-score) en vez de actuar como compuerta
todo-o-nada.

Para cada día en que la señal se cumple, medimos el retorno desde ese
cierre hasta el cierre `horizonte_dias` (hábiles) después, y agregamos:
número de señales, % de señales ganadoras, retorno promedio por señal,
y el retorno de comprar-y-mantener el periodo completo como referencia.
"""
import pandas as pd
import numpy as np

from acciones_extractor import obtener_historial
from indicadores import serie_rsi, serie_sma, serie_macd_hist

RSI_SOBREVENTA = 35
SMA_TENDENCIA = 150
MIN_DATOS = 180  # >SMA_TENDENCIA, con margen para que existan días señal válidos


def backtest_ticker(symbol: str, horizonte_dias: int = 21) -> dict | None:
    hist = obtener_historial(symbol)
    if hist.empty or len(hist) < MIN_DATOS:
        return None

    closes = hist["Close"]
    rsi = serie_rsi(closes)
    tendencia = serie_sma(closes, SMA_TENDENCIA)

    señal = (rsi < RSI_SOBREVENTA) & (closes > tendencia)
    retorno_fwd = closes.shift(-horizonte_dias) / closes - 1
    retornos_señal = retorno_fwd[señal].dropna()

    buy_hold = float(closes.iloc[-1] / closes.iloc[0] - 1)

    if retornos_señal.empty:
        return {
            "Ticker": symbol.replace(".MX", "").replace("BINANCE:", "").replace("USDT", ""),
            "N° señales": 0,
            "Retorno prom. por señal": None,
            "Tasa de aciertos": None,
            "Buy & Hold (periodo)": round(buy_hold * 100, 1),
        }

    return {
        "Ticker": symbol.replace(".MX", "").replace("BINANCE:", "").replace("USDT", ""),
        "N° señales": int(len(retornos_señal)),
        "Retorno prom. por señal": round(float(retornos_señal.mean()) * 100, 2),
        "Tasa de aciertos": round(float((retornos_señal > 0).mean()) * 100, 1),
        "Buy & Hold (periodo)": round(buy_hold * 100, 1),
    }


def evaluar_universo(tickers: list, horizonte_dias: int = 21) -> pd.DataFrame:
    filas = [backtest_ticker(t, horizonte_dias) for t in tickers]
    filas = [f for f in filas if f is not None]
    if not filas:
        return pd.DataFrame()
    df = pd.DataFrame(filas)
    return df.sort_values("N° señales", ascending=False)


def resumen_global(df: pd.DataFrame) -> dict:
    """Agrega todas las señales de todos los tickers en una sola estadística,
    ponderando cada señal por igual (no cada ticker por igual)."""
    if df.empty or "N° señales" not in df.columns:
        return {"total_señales": 0, "retorno_prom": None, "tasa_aciertos": None}

    con_señales = df[df["N° señales"] > 0]
    if con_señales.empty:
        return {"total_señales": 0, "retorno_prom": None, "tasa_aciertos": None}

    total_señales = con_señales["N° señales"].sum()
    retorno_ponderado = (con_señales["Retorno prom. por señal"] * con_señales["N° señales"]).sum() / total_señales
    aciertos_ponderado = (con_señales["Tasa de aciertos"] * con_señales["N° señales"]).sum() / total_señales

    return {
        "total_señales": int(total_señales),
        "retorno_prom": round(retorno_ponderado, 2),
        "tasa_aciertos": round(aciertos_ponderado, 1),
    }
