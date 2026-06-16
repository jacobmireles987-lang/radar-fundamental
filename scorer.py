"""
Score combinado: técnico + fundamental.

Filosofía del cambio respecto a la versión anterior:
- El score viejo premiaba sobre todo "momentum reciente" (cambio % del
  día, distancia al mínimo de 52 semanas) y eso es lo opuesto a "comprar
  barato": premiaba comprar lo que YA subió.
- El nuevo score separa dos cosas y las pondera por separado:
    1) Score Técnico  → ¿está el activo en una zona de entrada razonable
       según su propio historial de precio? (RSI, medias móviles, MACD)
    2) Score Fundamental → ¿es una empresa "barata" y sana según sus
       múltiplos y razones financieras? (P/E, P/B, ROE, deuda, crecimiento)
- Cada componente se normaliza con z-score CONTRA EL UNIVERSO actual de
  tickers (no contra un umbral fijo), lo que es más robusto: un solo
  ticker con un pico de volumen o una métrica rara ya no distorsiona la
  escala de todos los demás.
- Si un ticker no tiene datos fundamentales (cripto, o un ticker de BMV al
  que Finnhub no le da ciertas métricas en el plan gratuito), el score
  combinado cae automáticamente solo en el componente técnico, en vez de
  penalizarlo por datos faltantes.

Los pesos de abajo son los únicos números "a ojo" de todo el sistema.
Ajústalos con lo que veas en la pestaña de Backtesting — no son una
verdad matemática, son un punto de partida razonable.
"""
import numpy as np
import pandas as pd

PESO_TECNICO = 0.5
PESO_FUNDAMENTAL = 0.5

# Pesos relativos DENTRO del score técnico (deben sumar 1.0)
PESO_RSI = 0.40
PESO_TENDENCIA = 0.35
PESO_MACD = 0.25

# Pesos relativos DENTRO del score fundamental (se reescalan automáticamente
# si a algún ticker le faltan factores, ver _score_fundamental_puro)
PESOS_FUNDAMENTAL = {
    "P/E": 0.25,
    "P/B": 0.15,
    "ROE": 0.25,
    "Deuda/Capital": 0.15,
    "Crecimiento Ingresos": 0.15,
    "Dividend Yield": 0.05,
}

# Umbrales de señal sobre el Score combinado (0-100)
UMBRAL_COMPRA_FUERTE = 65
UMBRAL_COMPRA_MODERADA = 55
UMBRAL_VENTA = 45
UMBRAL_VENTA_FUERTE = 35


def score_fundamental(df: pd.DataFrame) -> pd.DataFrame:
    """Punto de entrada principal: recibe el DataFrame crudo de un grupo
    de tickers y regresa el mismo DataFrame con columnas de score y señal.
    (Se conserva el nombre de la función por compatibilidad con dashboard.py)
    """
    if df.empty:
        return df
    df = df.copy()

    tecnico = _score_tecnico(df)
    fundamental = _score_fundamental_puro(df)

    sin_fundamental = fundamental.isna()
    combinado = PESO_TECNICO * tecnico + PESO_FUNDAMENTAL * fundamental.fillna(0)
    combinado[sin_fundamental] = tecnico[sin_fundamental]

    df["Score Técnico"] = tecnico.round(1)
    df["Score Fundamental"] = fundamental.round(1)
    df["Score"] = combinado.round(1)
    df["Señal"] = df.apply(_senal, axis=1)

    return df.sort_values("Score", ascending=False)


def _z(serie: pd.Series) -> pd.Series:
    """Z-score de una serie. Si no hay variación (o solo hay un dato
    válido), regresa ceros en vez de dividir entre cero."""
    s = pd.to_numeric(serie, errors="coerce")
    mu, sd = s.mean(), s.std()
    if not sd or pd.isna(sd) or sd == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mu) / sd


def _a_0_100(z: pd.Series) -> pd.Series:
    """Convierte un z-score a escala 0-100 centrada en 50 (recorta a ±3σ)."""
    return (z.clip(-3, 3) + 3) / 6 * 100


def _score_tecnico(df: pd.DataFrame) -> pd.Series:
    rsi = pd.to_numeric(df.get("RSI"), errors="coerce")
    sma20 = pd.to_numeric(df.get("SMA20"), errors="coerce")
    sma50 = pd.to_numeric(df.get("SMA50"), errors="coerce")
    precio = pd.to_numeric(df["Precio"], errors="coerce")
    macd_hist = pd.to_numeric(df.get("MACD Hist"), errors="coerce")

    # RSI: zona de sobreventa (RSI bajo) puntúa alto = posible rebote;
    # zona de sobrecompra (RSI alto) puntúa bajo. Lineal entre RSI 10 y 70.
    score_rsi = ((70 - rsi).clip(0, 60) / 60 * 100).fillna(50)

    # Tendencia: ¿precio sobre su media de 20 y esa sobre la de 50?
    # (alineación alcista clásica). Cada condición vale 50 puntos.
    cond_precio_sma20 = (precio > sma20)
    cond_sma20_sma50 = (sma20 > sma50)
    tendencia = (
        cond_precio_sma20.where(cond_precio_sma20.notna() & sma20.notna(), other=np.nan).astype(float) * 50
        + cond_sma20_sma50.where(cond_sma20_sma50.notna() & sma50.notna(), other=np.nan).astype(float) * 50
    )
    tendencia = tendencia.fillna(50)

    # Momentum: histograma de MACD positivo y alto respecto al resto del
    # universo en este momento = impulso alcista relativo.
    score_macd = _a_0_100(_z(macd_hist)).fillna(50)

    return PESO_RSI * score_rsi + PESO_TENDENCIA * tendencia + PESO_MACD * score_macd


def _score_fundamental_puro(df: pd.DataFrame) -> pd.Series:
    factores = {
        "P/E": -_z(pd.to_numeric(df.get("P/E"), errors="coerce")),                       # menor P/E = mejor
        "P/B": -_z(pd.to_numeric(df.get("P/B"), errors="coerce")),                        # menor P/B = mejor
        "ROE": _z(pd.to_numeric(df.get("ROE"), errors="coerce")),                         # mayor ROE = mejor
        "Deuda/Capital": -_z(pd.to_numeric(df.get("Deuda/Capital"), errors="coerce")),    # menor deuda = mejor
        "Crecimiento Ingresos": _z(pd.to_numeric(df.get("Crecimiento Ingresos"), errors="coerce")),
        "Dividend Yield": _z(pd.to_numeric(df.get("Dividend Yield"), errors="coerce")),
    }

    disponibles_por_fila = pd.DataFrame({
        nombre: pd.to_numeric(df.get(nombre), errors="coerce").notna()
        for nombre in PESOS_FUNDAMENTAL
    })
    sin_ningun_dato = ~disponibles_por_fila.any(axis=1)

    # Si un factor no tiene al menos 2 valores válidos en TODO el grupo,
    # el z-score no es confiable (no hay con qué comparar) — lo excluimos.
    factores_usables = {
        nombre: serie for nombre, serie in factores.items()
        if pd.to_numeric(df.get(nombre), errors="coerce").notna().sum() >= 2
    }

    if not factores_usables:
        return pd.Series(np.nan, index=df.index)

    peso_total = sum(PESOS_FUNDAMENTAL[n] for n in factores_usables)
    score = sum(
        _a_0_100(serie).fillna(50) * PESOS_FUNDAMENTAL[nombre]
        for nombre, serie in factores_usables.items()
    ) / peso_total

    score = score.copy()
    score[sin_ningun_dato] = np.nan
    return score


def _senal(row: pd.Series) -> str:
    score = row["Score"]
    pe = row.get("P/E")
    mktcap = row.get("Mkt Cap")

    buen_per = pd.notna(pe) and 0 < pe <= 20
    micro_cap = pd.notna(mktcap) and 0 < mktcap <= 100

    if score >= UMBRAL_COMPRA_MODERADA and buen_per and micro_cap:
        return "💎 COMPRA IDEAL (MicroCap)"
    elif score >= UMBRAL_COMPRA_FUERTE:
        return "🔥 COMPRA FUERTE"
    elif score >= UMBRAL_COMPRA_MODERADA:
        return "⚡ COMPRA MODERADA"
    elif score <= UMBRAL_VENTA_FUERTE:
        return "🩸 VENTA FUERTE"
    elif score <= UMBRAL_VENTA:
        return "📉 VENTA"
    else:
        return "😴 NEUTRAL"


def fmt_mktcap(val) -> str:
    if pd.isna(val) or val == 0:
        return "—"
    try:
        v = float(val)
        if v >= 1e6:
            return f"${v/1e6:.1f}T"
        if v >= 1e3:
            return f"${v/1e3:.1f}B"
        return f"${v:,.0f}M"
    except Exception:
        return "—"


def fmt_num(val, decimals: int = 2) -> str:
    try:
        return f"{float(val):,.{decimals}f}"
    except Exception:
        return "—"
