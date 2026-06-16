import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

# Regresamos la API Key directa al código
API_KEY = "d8k6lmpr01qjgd6ruqs0d8k6lmpr01qjgd6ruqsg"

# Configuración de sesión robusta
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def obtener_fear_greed() -> dict:
    try:
        r = session.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        r.raise_for_status()
        data  = r.json()["data"][0]
        valor = int(data["value"])
        label = data["value_classification"]
        return {
            "valor" : valor,
            "label" : label,
            "emoji" : _emoji_fg(valor),
            "color" : _color_fg(valor),
        }
    except requests.exceptions.RequestException:
        return {"valor": 50, "label": "Neutral", "emoji": "😐", "color": "#FFA500"}

def obtener_noticias_mercado() -> list:
    try:
        r = session.get(
            "https://finnhub.io/api/v1/news",
            params={"category": "general", "token": API_KEY},
            timeout=10
        )
        r.raise_for_status()
        noticias_raw = r.json()[:6]
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
    except requests.exceptions.RequestException:
        return [{"titulo": "No se pudieron cargar las noticias del mercado", "fuente": "Sistema", "url": "#", "fecha": datetime.now().strftime('%Y-%m-%d')}]

def _emoji_fg(valor: int) -> str:
    if valor <= 25: return "😱"
    if valor <= 45: return "😨"
    if valor <= 55: return "😐"
    if valor <= 75: return "😊"
    return "🤑"

def _color_fg(valor: int) -> str:
    if valor <= 25: return "#dc2626"
    if valor <= 45: return "#f97316"
    if valor <= 55: return "#eab308"
    if valor <= 75: return "#84cc16"
    return "#16a34a"
