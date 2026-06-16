# radar-fundamental# radar-fundamental

Dashboard en Streamlit que rastrea BMV, NYSE/NASDAQ, penny stocks, acciones de beta elevada y cripto usando la API de Finnhub, y calcula un score combinado (técnico + fundamental) por cada ticker.

## Configuración de la API key

La clave de Finnhub **nunca** debe quedar escrita en el código (si el repo es público, queda expuesta para cualquiera). Se configura como secret:

- En Streamlit Cloud: *Manage app → Settings → Secrets*, con el formato:
```toml
  FINNHUB_API_KEY = "tu_clave_aquí"
```
- En local: crea `.streamlit/secrets.toml` con la misma línea (y agrégalo a `.gitignore`).
- Alternativa para scripts sueltos (ej. correr `backtest.py` desde la terminal sin Streamlit): variable de entorno `FINNHUB_API_KEY`.

## Cómo se calcula el Score

Cada ticker recibe dos sub-scores (0-100) que se promedian en un score final:

- **Score Técnico**: RSI(14), alineación de medias móviles (SMA20/SMA50) y momentum de MACD. Premia activos en zona de sobreventa dentro de una tendencia que sigue siendo favorable, no activos que ya subieron mucho.
- **Score Fundamental**: P/E, P/B, ROE, deuda/capital, crecimiento de ingresos y dividend yield, normalizados por z-score contra el resto del grupo (no contra un umbral fijo, así un solo dato atípico no distorsiona a todos los demás).

Si a un ticker le faltan datos fundamentales (cripto, o algún ticker internacional sin esa cobertura en el plan gratuito de Finnhub), el score cae automáticamente solo en la parte técnica en vez de penalizarlo.

Los pesos exactos están al inicio de `scorer.py` y son ajustables.

## Backtesting

La pestaña "🧪 Backtesting" valida **solo la componente técnica** contra precios históricos reales. La componente fundamental no se puede backtestear de forma honesta con el plan gratuito de Finnhub, porque la API solo entrega el valor *actual* de cada métrica (P/E, ROE, etc.), no su historia día por día.

**Importante**: esto muestra qué tan bien le habría ido a la señal técnica en el pasado. No es una garantía de rendimiento futuro ni asesoría de inversión.

## Límites de la API (plan gratuito)

Finnhub gratuito permite 60 llamadas/min. La app usa un limitador de tasa global (`rate_limiter.py`) y cachea en capas para no pasarse:

- Cotizaciones: cada 15 min.
- Fundamentales e historial de precios: cada 6 horas (no cambian intradía, y así el backtest reutiliza el mismo historial sin gastar llamadas extra).

La primera carga del día puede tardar 2-3 minutos mientras se llenan esos cachés de 6 horas; las recargas posteriores dentro de esa ventana son mucho más rápidas.

## Archivos

- `dashboard.py` — interfaz de Streamlit.
- `acciones_extractor.py` — llamadas a Finnhub (cotizaciones, fundamentales, historial).
- `sentimiento_extractor.py` — Fear & Greed y noticias.
- `indicadores.py` — RSI, medias móviles, MACD.
- `scorer.py` — score combinado y señales de compra/venta.
- `backtest.py` — validación histórica de la señal técnica.
- `rate_limiter.py` — limitador de tasa compartido para no exceder el límite de Finnhub.
- `components.py` — fragmentos HTML reutilizables para la tabla y tarjetas.
