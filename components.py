import pandas as pd

def tarjeta_fear_greed(fear_greed: dict) -> str:
    return f"""
    <div style="background:{fear_greed['color']}22;border:2px solid {fear_greed['color']};
    border-radius:12px;padding:14px;text-align:center">
    <div style="font-size:2rem">{fear_greed['emoji']}</div>
    <div style="font-size:1.4rem;font-weight:bold;color:{fear_greed['color']}">{fear_greed['valor']}/100</div>
    <div style="font-size:0.8rem;color:#666">Fear & Greed Cripto<br>{fear_greed['label']}</div>
    </div>"""

def tarjeta_oportunidad(nombre: str, mejor: pd.Series) -> str:
    senal = mejor['Señal']
    color_s = {
        "💎 COMPRA IDEAL (MicroCap)": "#8b5cf6",
        "🔥 COMPRA FUERTE": "#16a34a",
        "⚡ COMPRA MODERADA": "#2563eb",
        "🩸 VENTA FUERTE": "#7f1d1d",
        "📉 VENTA": "#dc2626",
        "😴 NEUTRAL": "#9ca3af"
    }.get(senal, "#333")

    return f"""
    <div style="background:#f8faff;border:1px solid #d1dcf0;
    border-radius:12px;padding:14px;text-align:center">
    <div style="font-size:0.75rem;color:#666">{nombre}</div>
    <div style="font-size:1.1rem;font-weight:bold">{mejor['Ticker']}</div>
    <div style="font-size:0.9rem;color:#1e3a5f">Score {mejor['Score']}</div>
    <div style="font-size:0.85rem;font-weight:bold;color:{color_s}">{senal}</div>
    </div>"""

def tarjeta_error() -> str:
    return """
    <div style="background:#fff5f5;border:1px solid #fed7d7;
    border-radius:12px;padding:14px;text-align:center">
    <div style="font-size:0.75rem;color:#e53e3e">Datos no disponibles</div>
    <div style="font-size:0.8rem">Límite de API alcanzado</div>
    </div>"""

def fila_tabla(row: pd.Series, fmt_num_func, fmt_mktcap_func) -> str:
    cambio  = row["Cambio %"]
    color_c = "#16a34a" if cambio >= 0 else "#dc2626"
    senal   = row["Señal"]

    color_s = {
        "💎 COMPRA IDEAL (MicroCap)": "#8b5cf6",
        "🔥 COMPRA FUERTE": "#16a34a",
        "⚡ COMPRA MODERADA": "#2563eb",
        "🩸 VENTA FUERTE": "#7f1d1d",
        "📉 VENTA": "#dc2626",
        "😴 NEUTRAL": "#9ca3af"
    }.get(senal, "#333")

    beta_str = f"{row['Beta']:.2f}" if pd.notna(row['Beta']) else "—"
    pe_str = f"{row['P/E']:.1f}" if pd.notna(row['P/E']) else "—"
    mkt_str = fmt_mktcap_func(row['Mkt Cap'])

    return (
        f"<tr><td><b>{row['Ticker']}</b></td>"
        f"<td style='font-size:12px'>{row['Nombre']}</td>"
        f"<td>${fmt_num_func(row['Precio'])}</td>"
        f"<td style='color:{color_c};font-weight:bold'>"
        f"{'▲' if cambio>=0 else '▼'} {fmt_num_func(abs(cambio))}%</td>"
        f"<td>{beta_str}</td><td>{pe_str}</td><td>{mkt_str}</td>"
        f"<td style='font-weight:bold;color:{color_s}'>{senal}</td>"
        f"<td style='font-weight:bold;color:#1e3a5f'>{row['Score']}</td></tr>"
    )

def css_tabla(ths: str, trs: str) -> str:
    return f"""
    <style>
    .ft{{width:100%;border-collapse:collapse;font-size:13px}}
    .ft th{{background:#1e3a5f;color:white;padding:8px 10px;text-align:left}}
    .ft tr:nth-child(even){{background:#f0f4ff}}
    .ft td{{padding:7px 10px;border-bottom:1px solid #e2e8f0}}
    </style>
    <table class="ft"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>
    """

def tarjeta_noticia(n: dict) -> str:
    return f"""
    <div style="background:#f8faff;border-left:4px solid #1e3a5f;
    padding:12px 16px;margin:8px 0;border-radius:0 8px 8px 0">
    <a href="{n['url']}" target="_blank" style="text-decoration:none;color:inherit;">
    <div style="font-weight:bold;font-size:1.1rem;">{n['titulo']}</div>
    </a>
    <div style="color:#666;font-size:12px;margin-top:4px;">{n['fuente']} · {n['fecha']}</div>
    </div>"""
