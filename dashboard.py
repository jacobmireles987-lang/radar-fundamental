import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time

from sentimiento_extractor import obtener_fear_greed, obtener_noticias_mercado
from scorer import score_fundamental, fmt_mktcap, fmt_num

API_KEY = "NTTE78R1NO78U4OV"

BMV       = ["AMXL.MX","FEMSAUBD.MX","BIMBOA.MX","WALMEX.MX","GMEXICOB.MX"]
NYSE      = ["AAPL","NVDA","MSFT","TSLA","META"]
PENNY     = ["SNDL","CLOV","GRAB","HIMS","SOFI"]
HIGH_BETA = ["RIOT","MARA","COIN","PLTR","HOOD"]
CRYPTO    = ["BTC","ETH","SOL","BNB","DOGE"]

st.set_page_config(page_title="Radar Fundamental", page_icon="📈", layout="wide")
st.title("📈 Radar de Análisis Fundamental")
st.caption("BMV · NYSE/NASDAQ · Penny Stocks · Beta Elevada · Cripto — Alpha Vantage")

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()

def obtener_quote(symbol):
    try:
        r = requests.get("https://www.alphavantage.co/query", params={
            "function": "GLOBAL_QUOTE",
            "symbol"  : symbol,
            "apikey"  : API_KEY,
        }, timeout=10)
        data = r.json().get("Global Quote", {})
        if not data:
            return {}
        precio = float(data.get("05. price", 0))
        cambio = float(data.get("10. change percent", "0%").replace("%",""))
        return {
            "Ticker"       : symbol.replace(".MX",""),
            "Nombre"       : symbol.replace(".MX",""),
            "Precio"       : round(precio, 2),
            "Cambio %"     : round(cambio, 2),
            "Volumen"      : int(data.get("06. volume", 0)),
            "52w Alto"     : float(data.get("03. high", 0)),
            "52w Bajo"     : float(data.get("04. low", 0)),
            "Beta"         : None,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
        }
    except Exception:
        return {}

def obtener_crypto(symbol):
    try:
        r = requests.get("https://www.alphavantage.co/query", params={
            "function"     : "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol,
            "to_currency"  : "USD",
            "apikey"       : API_KEY,
        }, timeout=10)
        data = r.json().get("Realtime Currency Exchange Rate", {})
        if not data:
            return {}
        precio = float(data.get("5. Exchange Rate", 0))
        return {
            "Ticker"       : symbol,
            "Nombre"       : data.get("1. From_Currency Name", symbol)[:20],
            "Precio"       : round(precio, 4),
            "Cambio %"     : 0.0,
            "Volumen"      : 0,
            "52w Alto"     : 0,
            "52w Bajo"     : 0,
            "Beta"         : None,
            "P/E"          : None,
            "Mkt Cap"      : None,
            "Recomendacion": "—",
        }
    except Exception:
        return {}

def obtener_historial(symbol):
    try:
        r = requests.get("https://www.alphavantage.co/query", params={
            "function"  : "TIME_SERIES_DAILY",
            "symbol"    : symbol,
            "outputsize": "compact",
            "apikey"    : API_KEY,
        }, timeout=10)
        data = r.json().get("Time Series (Daily)", {})
        if not data:
            return pd.DataFrame()
        rows = [{"Date": k, "Close": float(v["4. close"])}
                for k, v in list(data.items())[:60]]
        df = pd.DataFrame(rows)
        df["Date"] = pd.to_datetime(df["Date"])
        return df.sort_values("Date")
    except Exception:
        return pd.DataFrame()

def cargar_grupo(tickers, nombre, es_crypto=False):
    filas = []
    for t in tickers:
        dato = obtener_crypto(t) if es_crypto else obtener_quote(t)
        if dato:
            dato["Grupo"] = nombre
            filas.append(dato)
        time.sleep(0.3)
    return pd.DataFrame(filas) if filas else pd.DataFrame()

@st.cache_data(ttl=900, show_spinner=False)
def cargar_todos():
    grupos = {
        "BMV"      : cargar_grupo(BMV,       "🇲🇽 BMV"),
        "NYSE"     : cargar_grupo(NYSE,      "🇺🇸 NYSE/NASDAQ"),
        "Penny"    : cargar_grupo(PENNY,     "💰 Penny Stocks"),
        "High Beta": cargar_grupo(HIGH_BETA, "⚡ Beta Elevada"),
        "Crypto"   : cargar_grupo(CRYPTO,    "🪙 Cripto", es_crypto=True),
    }
    return grupos, obtener_fear_greed(), obtener_noticias_mercado()

with st.spinner("📡 Consultando mercados..."):
    grupos, fear_greed, noticias = cargar_todos()

st.divider()
c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(f"""
<div style="background:{fear_greed['color']}22;border:2px solid {fear_greed['color']};
border-radius:12px;padding:14px;text-align:center">
<div style="font-size:2rem">{fear_greed['emoji']}</div>
<div style="font-size:1.4rem;font-weight:bold;color:{fear_greed['color']}">{fear_greed['valor']}/100</div>
<div style="font-size:0.8rem;color:#666">Fear & Greed Cripto<br>{fear_greed['label']}</div>
</div>""", unsafe_allow_html=True)

for col,(nombre,df) in zip([c2,c3,c4,c5],list(grupos.items())[:4]):
    if not df.empty:
        scored = score_fundamental(df)
        mejor  = scored.iloc[0]
        col.markdown(f"""
<div style="background:#f8faff;border:1px solid #d1dcf0;
border-radius:12px;padding:14px;text-align:center">
<div style="font-size:0.75rem;color:#666">{nombre}</div>
<div style="font-size:1.1rem;font-weight:bold">{mejor['Ticker']}</div>
<div style="font-size:0.9rem;color:#16a34a">Score {mejor['Score']}</div>
<div style="font-size:0.8rem">{mejor['Señal']}</div>
</div>""", unsafe_allow_html=True)

st.divider()
tabs = st.tabs(["🇲🇽 BMV","🇺🇸 NYSE/NASDAQ","💰 Penny Stocks","⚡ Beta Elevada","🪙 Cripto","📰 Noticias","🔍 Buscador"])

def render_grupo(df_raw, tab, key):
    with tab:
        if df_raw.empty:
            st.warning("⚠️ Sin datos. Límite de API alcanzado. Intenta en unos minutos.")
            return
        df = score_fundamental(df_raw)
        st.subheader("📊 Tabla de Oportunidades")

        def fila_html(row):
            cambio  = row["Cambio %"]
            color_c = "#16a34a" if cambio >= 0 else "#dc2626"
            senal   = row["Señal"]
            color_s = {"🔥 FUERTE":"#16a34a","⚡ MODERADA":"#2563eb",
                       "👀 OBSERVAR":"#d97706","😴 DÉBIL":"#9ca3af"}.get(senal,"#333")
            return (
                f"<tr><td><b>{row['Ticker']}</b></td>"
                f"<td style='font-size:12px'>{row['Nombre']}</td>"
                f"<td>${fmt_num(row['Precio'])}</td>"
                f"<td style='color:{color_c};font-weight:bold'>{'▲' if cambio>=0 else '▼'} {fmt_num(abs(cambio))}%</td>"
                f"<td>—</td><td>—</td><td>—</td>"
                f"<td style='font-weight:bold;color:{color_s}'>{senal}</td>"
                f"<td style='font-weight:bold;color:#1e3a5f'>{row['Score']}</td></tr>"
            )

        ths = "".join(f"<th>{h}</th>" for h in ["Ticker","Nombre","Precio","Cambio %","Beta","P/E","Mkt Cap","Señal","Score"])
        trs = "".join(fila_html(r) for _,r in df.iterrows())
        st.markdown(f"""
<style>
.ft{{width:100%;border-collapse:collapse;font-size:13px}}
.ft th{{background:#1e3a5f;color:white;padding:8px 10px;text-align:left}}
.ft tr:nth-child(even){{background:#f0f4ff}}
.ft td{{padding:7px 10px;border-bottom:1px solid #e2e8f0}}
</style>
<table class="ft"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)
        with col1:
            st.subheader("🏆 Score de Oportunidad")
            fig = px.bar(df.sort_values("Score"), x="Score", y="Ticker",
                        orientation="h", color="Score",
                        color_continuous_scale="RdYlGn", text="Score")
            fig.update_layout(height=300,plot_bgcolor="white",showlegend=False,
                             yaxis=dict(autorange="reversed"))
            fig.update_traces(texttemplate="%{text}",textposition="outside")
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
            fig2.update_layout(height=300,plot_bgcolor="white",
                              xaxis=dict(zeroline=True,zerolinecolor="#333"))
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

render_grupo(grupos["BMV"],       tabs[0], "bmv")
render_grupo(grupos["NYSE"],      tabs[1], "nyse")
render_grupo(grupos["Penny"],     tabs[2], "penny")
render_grupo(grupos["High Beta"], tabs[3], "hbeta")
render_grupo(grupos["Crypto"],    tabs[4], "crypto")

with tabs[5]:
    st.subheader("📰 Noticias del Mercado")
    for n in noticias:
        st.markdown(f"""
<div style="background:#f8faff;border-left:4px solid #1e3a5f;
padding:12px 16px;margin:8px 0;border-radius:0 8px 8px 0">
<div style="font-weight:bold">{n['titulo']}</div>
<div style="color:#666;font-size:12px">{n['fuente']} · {n['fecha']}</div>
</div>""", unsafe_allow_html=True)

with tabs[6]:
    st.subheader("🔍 Busca cualquier activo")
    st.caption("Ejemplos: AAPL, TSLA, AMXL.MX, BTC")
    col_inp,col_btn = st.columns([3,1])
    with col_inp:
        ticker_input = st.text_input("Ticker:", placeholder="Ej: TSLA")
    with col_btn:
        buscar = st.button("🔍 Buscar", use_container_width=True)

    if buscar and ticker_input:
        with st.spinner(f"Buscando {ticker_input.upper()}..."):
            dato = obtener_quote(ticker_input.upper())
        if dato:
            st.success(f"✅ {dato['Ticker']}")
            c1,c2,c3 = st.columns(3)
            c1.metric("💵 Precio",   f"${fmt_num(dato['Precio'])}")
            c2.metric("📊 Cambio %", f"{dato['Cambio %']:+.2f}%")
            c3.metric("📦 Volumen",  f"{dato['Volumen']:,}")
            with st.spinner("Cargando historial..."):
                hist = obtener_historial(ticker_input.upper())
            if not hist.empty:
                fig = px.line(hist, x="Date", y="Close",
                             title=f"{ticker_input.upper()} — 60 días")
                fig.update_layout(plot_bgcolor="white", height=350)
                fig.update_traces(line_color="#1e3a5f", line_width=2)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"No se encontró '{ticker_input}'.")

st.divider()
st.caption("Alpha Vantage API · Fear & Greed Alternative.me · Solo informativo, no es consejo de inversión.")
