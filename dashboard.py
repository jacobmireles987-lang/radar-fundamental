import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sentimiento_extractor import obtener_fear_greed, obtener_noticias_mercado
from scorer import score_fundamental, fmt_mktcap, fmt_num
import acciones_extractor
from acciones_extractor import obtener_todos, obtener_quote, obtener_historial
import backtest
import components

st.set_page_config(page_title="Radar Fundamental", page_icon="📈", layout="wide")
st.title("📈 Radar de Análisis Fundamental")
st.caption("BMV · NYSE/NASDAQ · Penny Stocks · Beta Elevada · Cripto — Finnhub API")
st.caption("Score = Técnico (RSI, medias móviles, MACD) + Fundamental (P/E, P/B, ROE, deuda, crecimiento). Solo informativo, no es consejo de inversión ni garantía de rendimiento.")

if st.button("🔄 Actualizar cotizaciones"):
    # Solo limpiamos el caché de cotizaciones (15 min). Los fundamentales y
    # el historial de precios (6 h) NO se limpian aquí a propósito: son los
    # que más llamadas a la API consumen y no cambian de un minuto a otro.
    # Si de verdad quieres forzar todo desde cero, usa el botón de abajo.
    cargar_todos.clear()
    st.rerun()

with st.expander("⚙️ Forzar recarga completa (fundamentales + historial)"):
    st.caption("Solo necesario si crees que algún dato fundamental quedó desactualizado. Esto consume muchas más llamadas a la API y puede tardar 2-3 minutos en el plan gratuito.")
    if st.button("🧹 Limpiar todo el caché y recargar"):
        st.cache_data.clear()
        st.rerun()


@st.cache_data(ttl=900, show_spinner=False)
def cargar_todos():
    return obtener_todos(), obtener_fear_greed(), obtener_noticias_mercado()

with st.spinner("📡 Consultando mercados y calculando scores..."):
    grupos, fear_greed, noticias = cargar_todos()

# ── FEAR & GREED ─────────────────────────────────────────────
st.divider()
c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(components.tarjeta_fear_greed(fear_greed), unsafe_allow_html=True)

for col,(nombre,df) in zip([c2,c3,c4,c5],list(grupos.items())[:4]):
    if not df.empty:
        scored = score_fundamental(df)
        mejor  = scored.iloc[0]
        col.markdown(components.tarjeta_oportunidad(nombre, mejor), unsafe_allow_html=True)
    else:
        col.markdown(components.tarjeta_error(), unsafe_allow_html=True)

st.divider()

# ── TABS ─────────────────────────────────────────────────────
tabs = st.tabs(["🇲🇽 BMV","🇺🇸 NYSE/NASDAQ","💰 Penny Stocks",
                "⚡ Beta Elevada","🪙 Cripto","📰 Noticias","🔍 Buscador","🧪 Backtesting"])

def render_grupo(df_raw, tab, key):
    with tab:
        if df_raw.empty:
            st.warning("⚠️ Sin datos disponibles en este momento. Intenta actualizar en un minuto (Límite de API).")
            return
        df = score_fundamental(df_raw)
        st.subheader("📊 Tabla de Oportunidades")

        ths = "".join(f"<th>{h}</th>" for h in
                      ["Ticker","Nombre","Precio","Cambio %","Beta","P/E","Mkt Cap","Señal","Score"])
        trs = "".join(components.fila_tabla(r, fmt_num, fmt_mktcap) for _,r in df.iterrows())
        st.markdown(components.css_tabla(ths, trs), unsafe_allow_html=True)
        st.caption("El Score combina técnico + fundamental. Para ver el desglose de cada uno, selecciona el activo abajo.")

        st.markdown("<br>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Score de Oportunidad")
            fig = px.bar(df.sort_values("Score"), x="Score", y="Ticker",
                        orientation="h", color="Score",
                        color_continuous_scale="RdYlGn", text="Score")
            fig.update_layout(height=350, plot_bgcolor="white", showlegend=False,
                             yaxis=dict(autorange="reversed"))
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📉 Cambio % del día")
            colores = ["#16a34a" if v>=0 else "#dc2626" for v in df["Cambio %"]]
            fig2 = go.Figure(go.Bar(
                x=df["Cambio %"], y=df["Ticker"], orientation="h",
                marker_color=colores,
                text=df["Cambio %"].apply(lambda x: f"{x:+.2f}%"),
                textposition="outside",
            ))
            fig2.update_layout(height=350, plot_bgcolor="white",
                              xaxis=dict(zeroline=True, zerolinecolor="#333"))
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📡 Detalle por activo")
        ticker_sel = st.selectbox("Selecciona:", df["Ticker"].tolist(), key=f"sel_{key}")
        fila = df[df["Ticker"]==ticker_sel].iloc[0]
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("💵 Precio",   f"${fmt_num(fila['Precio'])}")
        m2.metric("📊 Cambio %", f"{fila['Cambio %']:+.2f}%")
        m3.metric("📐 Técnico",  fila["Score Técnico"])
        m4.metric("📋 Fundamental", fila["Score Fundamental"] if pd.notna(fila["Score Fundamental"]) else "—")
        m5.metric("🏆 Score",    fila["Score"])
        m6.metric("📌 Señal",    fila["Señal"])

        with st.spinner("Cargando historial..."):
            hist = obtener_historial(ticker_sel)
        if not hist.empty:
            fig3 = px.line(hist.tail(60), x="Date", y="Close",
                          title=f"{ticker_sel} — Precio 60 días")
            fig3.update_layout(plot_bgcolor="white", height=300)
            fig3.update_traces(line_color="#1e3a5f", line_width=2)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Historial no disponible para este activo o límite de consultas alcanzado.")

render_grupo(grupos["BMV"],       tabs[0], "bmv")
render_grupo(grupos["NYSE"],      tabs[1], "nyse")
render_grupo(grupos["Penny"],     tabs[2], "penny")
render_grupo(grupos["High Beta"], tabs[3], "hbeta")
render_grupo(grupos["Crypto"],    tabs[4], "crypto")

with tabs[5]:
    st.subheader("📰 Noticias del Mercado (Tiempo Real)")
    for n in noticias:
        st.markdown(components.tarjeta_noticia(n), unsafe_allow_html=True)

with tabs[6]:
    st.subheader("🔍 Busca cualquier activo")
    st.caption("Ejemplos: AAPL, TSLA, AMXL.MX, BINANCE:BTCUSDT")
    col_inp,col_btn = st.columns([3,1])
    with col_inp:
        ticker_input = st.text_input("Ticker:", placeholder="Ej: TSLA")
    with col_btn:
        buscar = st.button("🔍 Buscar", use_container_width=True)

    if buscar and ticker_input:
        with st.spinner(f"Buscando {ticker_input.upper()}..."):
            dato = obtener_quote(ticker_input.upper())
        if dato and "error" not in dato:
            st.success(f"✅ {dato['Ticker']}")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("💵 Precio",   f"${fmt_num(dato['Precio'])}")
            c2.metric("📊 Cambio %", f"{dato['Cambio %']:+.2f}%")
            c3.metric("📌 P/E",    f"{dato['P/E']}" if dato['P/E'] else "—")
            c4.metric("📐 RSI",    f"{dato['RSI']:.0f}" if dato.get('RSI') is not None and pd.notna(dato['RSI']) else "—")
            with st.spinner("Cargando historial..."):
                hist = obtener_historial(ticker_input.upper())
            if not hist.empty:
                fig = px.line(hist.tail(60), x="Date", y="Close",
                             title=f"{ticker_input.upper()} — 60 días")
                fig.update_layout(plot_bgcolor="white", height=350)
                fig.update_traces(line_color="#1e3a5f", line_width=2)
                st.plotly_chart(fig, use_container_width=True)
        elif dato.get("error") == "rate_limit":
            st.error("⚠️ Límite de consultas a la API alcanzado. Espera un momento.")
        else:
            st.error(f"No se encontró '{ticker_input}'.")

with tabs[7]:
    st.subheader("🧪 Backtesting de la señal técnica")
    st.markdown(
        "Esto evalúa **únicamente la parte técnica** de la estrategia (RSI + tendencia de "
        "largo plazo) contra precios históricos reales. La parte fundamental no se puede "
        "backtestear de forma honesta con el plan gratuito de Finnhub, porque solo entrega "
        "el valor *actual* de cada métrica (P/E, ROE, etc.), no su historia día por día — "
        "aplicar el dato de hoy a una fecha pasada sería un backtest inválido."
    )

    grupos_disponibles = {
        "🇲🇽 BMV": acciones_extractor.BMV,
        "🇺🇸 NYSE/NASDAQ": acciones_extractor.NYSE,
        "💰 Penny Stocks": acciones_extractor.PENNY,
        "⚡ Beta Elevada": acciones_extractor.HIGH_BETA,
        "🪙 Cripto": acciones_extractor.CRYPTO,
    }
    seleccion = st.multiselect("Universo a evaluar:", list(grupos_disponibles.keys()),
                                default=list(grupos_disponibles.keys()))

    opciones_horizonte = {
        "1 semana (~5 días hábiles)": 5,
        "2 semanas (~10 días hábiles)": 10,
        "1 mes (~21 días hábiles)": 21,
    }
    horizonte_label = st.selectbox("Horizonte tras la señal:", list(opciones_horizonte.keys()), index=2)
    horizonte_dias = opciones_horizonte[horizonte_label]

    if st.button("▶️ Ejecutar backtest"):
        tickers_evaluar = [t for g in seleccion for t in grupos_disponibles[g]]
        if not tickers_evaluar:
            st.warning("Selecciona al menos un grupo.")
        else:
            with st.spinner(f"Evaluando {len(tickers_evaluar)} tickers (reutiliza el historial ya en caché; "
                             f"si está frío puede tardar uno o dos minutos por el límite del plan gratuito)..."):
                resultado = backtest.evaluar_universo(tickers_evaluar, horizonte_dias=horizonte_dias)

            if resultado.empty:
                st.warning("No hay suficiente historial de precios todavía para los tickers seleccionados "
                           "(se necesitan al menos ~180 días de velas). Intenta de nuevo en unos minutos.")
            else:
                resumen = backtest.resumen_global(resultado)
                if resumen["total_señales"] == 0:
                    st.info("La señal técnica no se activó ninguna vez en el historial disponible para este "
                            "universo. Eso también es información válida: no hubo oportunidades claras según "
                            "estos criterios, no es un error del sistema.")
                else:
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Señales totales", resumen["total_señales"])
                    c2.metric("Retorno prom. por señal", f"{resumen['retorno_prom']:+.2f}%")
                    c3.metric("Tasa de aciertos", f"{resumen['tasa_aciertos']:.1f}%")

                st.dataframe(resultado, use_container_width=True, hide_index=True)

    st.caption("⚠️ Esto es un resultado histórico sobre datos pasados, no una promesa de rendimiento futuro. "
               "El comportamiento del mercado cambia, y que una señal haya funcionado antes no garantiza "
               "que vuelva a hacerlo.")

st.divider()
st.caption("Finnhub API · Fear & Greed Alternative.me · Solo informativo, no es consejo de inversión.")
