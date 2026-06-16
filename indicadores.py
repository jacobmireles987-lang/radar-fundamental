"""
Indicadores técnicos calculados a partir de una serie de precios de cierre.

Cada indicador tiene dos versiones:
- `serie_*`  → devuelve la serie completa (un valor por cada día), usada
  por el backtest para simular señales día por día.
- `calcular_*` → devuelve solo el último valor, usado para el score "en
  vivo" del dashboard.
"""
import numpy as np
import pandas as pd


def serie_rsi(closes: pd.Series, periodo: int = 14) -> pd.Series:
    """RSI de Wilder, devuelto como serie completa."""
    delta = closes.diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    avg_ganancia = ganancia.ewm(alpha=1 / periodo, min_periods=periodo).mean()
    avg_perdida = perdida.ewm(alpha=1 / periodo, min_periods=periodo).mean()
    rs = avg_ganancia / avg_perdida.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def serie_sma(closes: pd.Series, ventana: int) -> pd.Series:
    return closes.rolling(ventana).mean()


def serie_macd_hist(closes: pd.Series, rapida: int = 12, lenta: int = 26, señal: int = 9) -> pd.Series:
    ema_rapida = closes.ewm(span=rapida, adjust=False).mean()
    ema_lenta = closes.ewm(span=lenta, adjust=False).mean()
    macd = ema_rapida - ema_lenta
    linea_señal = macd.ewm(span=señal, adjust=False).mean()
    return macd - linea_señal


def calcular_rsi(closes: pd.Series, periodo: int = 14) -> float:
    if len(closes) < periodo + 1:
        return np.nan
    s = serie_rsi(closes, periodo)
    return float(s.iloc[-1]) if len(s) and pd.notna(s.iloc[-1]) else np.nan


def calcular_sma(closes: pd.Series, ventana: int) -> float:
    if len(closes) < ventana:
        return np.nan
    s = serie_sma(closes, ventana)
    return float(s.iloc[-1]) if len(s) and pd.notna(s.iloc[-1]) else np.nan


def calcular_macd_hist(closes: pd.Series, rapida: int = 12, lenta: int = 26, señal: int = 9) -> float:
    if len(closes) < lenta + señal:
        return np.nan
    s = serie_macd_hist(closes, rapida, lenta, señal)
    return float(s.iloc[-1]) if len(s) and pd.notna(s.iloc[-1]) else np.nan


def analizar_serie(closes: pd.Series) -> dict:
    """Devuelve el snapshot más reciente de los indicadores técnicos
    de una serie de precios de cierre. Tolerante a series cortas: si no
    hay suficiente historial, regresa NaN en vez de fallar."""
    closes = pd.to_numeric(closes, errors="coerce").dropna()
    return {
        "RSI": calcular_rsi(closes),
        "SMA20": calcular_sma(closes, 20),
        "SMA50": calcular_sma(closes, 50),
        "MACD Hist": calcular_macd_hist(closes),
    }
