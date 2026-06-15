import pandas as pd
import numpy as np

def score_fundamental(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula un score fundamental y emite señales de compra/venta basadas en 
    múltiplos (PER), capitalización (Mkt Cap <= 100M) e indicadores técnicos.
    """
    if df.empty:
        return df
    df = df.copy()
    
    # Aseguramos que los datos sean numéricos
    beta    = pd.to_numeric(df["Beta"], errors="coerce").fillna(1.0)
    vol     = pd.to_numeric(df["Volumen"], errors="coerce").fillna(0)
    cambio  = pd.to_numeric(df["Cambio %"], errors="coerce").fillna(0)
    precio  = pd.to_numeric(df["Precio"], errors="coerce").fillna(0)
    bajo_52 = pd.to_numeric(df["52w Bajo"], errors="coerce").fillna(0)
    pe      = pd.to_numeric(df["P/E"], errors="coerce").fillna(15) 
    mktcap  = pd.to_numeric(df["Mkt Cap"], errors="coerce").fillna(0)
    
    distancia = (precio - bajo_52) / precio.replace(0, np.nan)

    # Cálculo del Score Base (0 a 100)
    score_volumen = _normalizar(vol) * 20
    score_cambio = _normalizar(cambio) * 30
    score_distancia = (1 - _normalizar(distancia.fillna(0.5))) * 25
    score_pe = np.where((pe > 0) & (pe <= 20), 25, np.where((pe > 20) & (pe < 50), 10, 0))
    
    df["Score"] = (score_volumen + score_cambio + score_distancia + score_pe).round(1)
    
    # Aplicamos la lógica de señales evaluando toda la fila
    df["Señal"] = df.apply(_senal_avanzada, axis=1)
    
    return df.sort_values("Score", ascending=False)

def _normalizar(serie: pd.Series) -> pd.Series:
    """Normaliza una serie de Pandas de 0 a 1."""
    mn, mx = serie.min(), serie.max()
    if mx == mn:
        return pd.Series(np.ones(len(serie)), index=serie.index)
    return (serie - mn) / (mx - mn)

def _senal_avanzada(row: pd.Series) -> str:
    """Cruza los indicadores para emitir la recomendación final."""
    score = row["Score"]
    pe = row["P/E"]
    mktcap = row["Mkt Cap"]
    
    # Criterios solicitados:
    buen_per = pd.notna(pe) and 0 < pe <= 20
    micro_cap = pd.notna(mktcap) and mktcap <= 100 and mktcap > 0
    
    # Emisión de señales
    if score >= 70 and buen_per and micro_cap:
        return "💎 COMPRA IDEAL (MicroCap)"
    elif score >= 75:
        return "🔥 COMPRA FUERTE"
    elif score >= 55:
        return "⚡ COMPRA MODERADA"
    elif score <= 30:
        return "🩸 VENTA FUERTE"
    elif score <= 45:
        return "📉 VENTA"
    else:
        return "😴 NEUTRAL"

def fmt_mktcap(val) -> str:
    if pd.isna(val) or val == 0:
        return "—"
    try:
        v = float(val)
        if v >= 1e6: return f"${v/1e6:.1f}T" 
        if v >= 1e3: return f"${v/1e3:.1f}B"
        return f"${v:,.0f}M"
    except Exception:
        return "—"

def fmt_num(val, decimals: int = 2) -> str:
    try:
        return f"{float(val):,.{decimals}f}"
    except Exception:
        return "—"
