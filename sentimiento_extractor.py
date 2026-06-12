import requests
from datetime import datetime

API_KEY = "d8k6lmpr01qjgd6ruqs0d8k6lmpr01qjgd6ruqsg"

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
    try:
        r = requests.get(
            "https://finnhub.io/api/v1/news",
            params={"category": "general", "token": API_KEY},
            timeout=10
        )
        if r.status_code == 200:
            noticias_raw = r.json()[:6] # Tomamos solo las últimas 6 noticias
            noticias_formateadas = []
            for n in noticias_raw:
                fecha_str = datetime.fromtimestamp(n.get("datetime", 0)).strftime('%Y-%m-%d %H:%M')
                noticias_formateadas.append({
                    "titulo": n.get("headline", "Sin titular"),
                    "fuente": n.get("source", "Desconocido"),
                    "url": n.get("url", "#"),
                    "fecha": fecha_str
                })
            return noticias_formateadas
    except Exception:
        pass
        
    return [{"titulo": "No se pudieron cargar las noticias del mercado", "fuente": "Sistema", "url": "#", "fecha": datetime.now().strftime('%Y-%m-%d')}]

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
