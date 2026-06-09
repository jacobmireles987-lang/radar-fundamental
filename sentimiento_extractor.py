import requests
import pandas as pd

def obtener_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        if r.status_code == 200:
            data  = r.json()["data"][0]
            valor = int(data["value"])
            label = data["value_classification"]
            return {
                "valor" : valor,
                "label" : label,
                "emoji" : _emoji_fg(valor),
                "color" : _color_fg(valor),
            }
    except Exception:
        pass
    return {"valor": 50, "label": "Neutral", "emoji": "😐", "color": "#FFA500"}

def obtener_noticias_mercado():
    return [
        {"titulo": "Mercados al alza por datos de empleo en EE.UU.",
         "fuente": "El Financiero", "url": "#", "fecha": "2026-06-09"},
        {"titulo": "Bitcoin supera resistencia clave",
         "fuente": "CriptoNoticias", "url": "#", "fecha": "2026-06-09"},
        {"titulo": "BMV cierra con ganancias lideradas por AMXL",
         "fuente": "El Economista", "url": "#", "fecha": "2026-06-09"},
        {"titulo": "Penny stocks disparan volumen en sesión volátil",
         "fuente": "Investing.com", "url": "#", "fecha": "2026-06-09"},
        {"titulo": "Fed mantiene tasas: impacto en bolsas emergentes",
         "fuente": "Bloomberg MX", "url": "#", "fecha": "2026-06-09"},
        {"titulo": "NVDA alcanza nuevo máximo histórico",
         "fuente": "Reuters", "url": "#", "fecha": "2026-06-09"},
    ]

def _emoji_fg(valor):
    if valor <= 25: return "😱"
    if valor <= 45: return "😨"
    if valor <= 55: return "😐"
    if valor <= 75: return "😊"
    return "🤑"

def _color_fg(valor):
    if valor <= 25: return "#dc2626"
    if valor <= 45: return "#f97316"
    if valor <= 55: return "#eab308"
    if valor <= 75: return "#84cc16"
    return "#16a34a"
