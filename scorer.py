import pandas as pd
import numpy as np

def score_fundamental(df):
    if df.empty:
        return df
    df = df.copy()
    beta   = pd.to_numeric(df["Beta"],    errors="coerce").fillna(1.0)
    vol    = pd.to_numeric(df["Volumen"], errors="coerce").fillna(0)
    cambio = pd.to_numeric(df["Cambio %"],errors="coerce").fillna(0)
    precio  = pd.to_numeric(df["Precio"],   errors="coerce").fillna(0)
    bajo_52 = pd.to_numeric(df["52w Bajo"], errors="coerce").fillna(0)
    distancia = (precio - bajo_52) / precio.replace(0, np.nan)

    df["Score"] = (
        _normalizar(beta)                        * 25 +
        _normalizar(vol)                         * 25 +
        _normalizar(cambio)                      * 25 +
        (1 - _normalizar(distancia.fillna(0.5))) * 25
    ).round(1)

    df["Señal"] = df["Score"].apply(_senal)
    return df.sort_values("Score", ascending=False)

def _normalizar(serie):
    mn, mx = serie.min(), serie.max()
    if mx == mn:
        return pd.Series(np.ones(len(serie)), index=serie.index)
    return (serie - mn) / (mx - mn)

def _senal(score):
    if score >= 75: return "🔥 FUERTE"
    if score >= 55: return "⚡ MODERADA"
    if score >= 35: return "👀 OBSERVAR"
    return "😴 DÉBIL"

def fmt_mktcap(val):
    try:
        v = float(val)
        if v >= 1e12: return f"${v/1e12:.1f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        if v >= 1e6:  return f"${v/1e6:.1f}M"
        return f"${v:,.0f}"
    except Exception:
        return "—"

def fmt_num(val, decimals=2):
    try:
        return f"{float(val):,.{decimals}f}"
    except Exception:
        return "—"
