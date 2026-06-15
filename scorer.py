# scorer.py
import pandas as pd
import numpy as np

def score_fundamental(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula un score fundamental basado en volumen, cambio, distancia al bajo de 52 semanas y P/E.
    Devuelve un DataFrame ordenado por Score descendente.
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
    
    distancia = (precio - bajo_52) / precio.replace(0, np.nan)

    score_volumen = _normalizar(vol) * 20
    score_cambio = _normalizar(cambio) * 30
    score_distancia = (1 - _normalizar(distancia.fillna(0.5))) * 25
    
    score_pe = np.where((pe > 0) & (pe < 30), 25, np.where((pe >= 30) & (pe < 50), 10, 0))
    
    df["Score"] = (score_volumen + score_cambio + score_distancia + score_pe).round(1)
    df["Señal"] = df["Score"].apply(_senal)
    
    return df.sort_values("Score", ascending=False)

def _normalizar(serie: pd.Series) -> pd.Series:
    """Normaliza una serie de Pandas de 0 a 1."""
    mn, mx = serie.min(), serie.max()
    if mx == mn:
        return pd.Series(np.ones(len(serie)), index=serie.index)
    return (serie - mn) / (mx - mn)

def _senal(score: float) -> str:
    """Devuelve un emoji y una etiqueta en texto según el score calculado."""
    if score >= 75: return "🔥 FUERTE"
    if score >= 55: return "⚡ MODERADA"
    if score >= 35: return "👀 OBSERVAR"
    return "😴 DÉBIL"

def fmt_mktcap(val) -> str:
    """Formatea la capitalización de mercado para una fácil lectura."""
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
    """Convierte un valor numérico a un string con formato de moneda."""
    try:
        return f"{float(val):,.{decimals}f}"
    except Exception:
        return "—"
