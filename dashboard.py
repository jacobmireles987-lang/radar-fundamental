import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sentimiento_extractor import obtener_fear_greed, obtener_noticias_mercado
from scorer import score_fundamental, fmt_mktcap, fmt_num
from acciones_extractor import (obtener_todos, obtener_quote, API_KEY)
import components

st.set_page_config(page_title="Radar Fundamental", page_icon="📈", layout="wide")
st.title("📈 Radar de Análisis Fundamental")
st.caption("BMV · NYSE/NASDAQ · Penny Stocks · Beta Elevada · Cripto — Finnhub API")

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()

# Configurar sesión con reintentos para la gráfica
session_hist = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session_hist.mount('https://', HTTPAdapter(max_retries=retries))

def obtener_historial(symbol: str) -> pd.DataFrame:
    import time as t
    try:
        ahora  = int(t.time())
        inicio = ahora - 60 * 24 * 3600  # 60 días
        r = session_hist.get(
            "https://finnhub.io/api/v1/stock/candle",
            params={
                "symbol"    : symbol,
                "resolution": "D",
                "from"      : inicio,
                "to"        : ahora,
                "token"     : API_KEY,
            },
            timeout=10
        )
        if r.status_code == 429:
            st.toast("⚠️ Límite de API alcanzado al cargar el gráfico.", icon="⏳")
            return pd.DataFrame()
            
        r.raise_for_status()
        data = r.json()
        if data.get("s") != "ok":
            return pd.DataFrame()
        df = pd.DataFrame({
            "Date" : pd.to_datetime(data["t"], unit="s"),
            "Close": data["c"],
        })
        return df.sort_values("Date")
    except requests.exceptions.RequestException:
        return pd.DataFrame()

@st.cache_data(ttl=900, show_spinner=False)
def cargar_todos():
    return obtener_todos(), obtener_fear_greed(), obtener_noticias_mercado()

with st.spinner("📡 Consultando mercados y calculando fundamentales..."):
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
                "⚡ Beta Elevada","🪙 Cripto","📰 Noticias","🔍 Buscador"])

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
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("💵 Precio",   f"${fmt_num(fila['Precio'])}")
        m2.metric("📊 Cambio %", f"{fila['Cambio %']:+.2f}%")
        m3.metric("🏆 Score",    fila["Score"])
        m4.metric("📌 Señal",    fila["Señal"])

        with st.spinner("Cargando historial..."):
            hist = obtener_historial(ticker_sel)
        if not hist.empty:
            fig3 = px.line(hist, x="Date", y="Close",
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
            c1,c2,c3 = st.columns(3)
            c1.metric("💵 Precio",   f"${fmt_num(dato['Precio'])}")
            c2.metric("📊 Cambio %", f"{dato['Cambio %']:+.2f}%")
            c3.metric("📌 P/E",    f"{dato['P/E']}" if dato['P/E'] else "—")
            with st.spinner("Cargando historial..."):
                hist = obtener_historial(ticker_input.upper())
            if not hist.empty:
                fig = px.line(hist, x="Date", y="Close",
                             title=f"{ticker_input.upper()} — 60 días")
                fig.update_layout(plot_bgcolor="white", height=350)
                fig.update_traces(line_color="#1e3a5f", line_width=2)
                st.plotly_chart(fig, use_container_width=True)
        elif dato.get("error") == "rate_limit":
            st.error("⚠️ Límite de consultas a la API alcanzado. Espera un momento.")
        else:
            st.error(f"No se encontró '{ticker_input}'.")

st.divider()
st.caption("Finnhub API · Fear & Greed Alternative.me · Solo informativo, no es consejo de inversión.")
