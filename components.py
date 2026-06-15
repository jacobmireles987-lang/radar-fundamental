def fila_tabla(row: pd.Series, fmt_num_func, fmt_mktcap_func) -> str:
    cambio  = row["Cambio %"]
    color_c = "#16a34a" if cambio >= 0 else "#dc2626"
    senal   = row["Señal"]
    
    # Diccionario de colores actualizado para las nuevas señales
    color_s = {
        "💎 COMPRA IDEAL (MicroCap)": "#8b5cf6", # Morado distintivo
        "🔥 COMPRA FUERTE": "#16a34a",           # Verde fuerte
        "⚡ COMPRA MODERADA": "#2563eb",         # Azul
        "🩸 VENTA FUERTE": "#7f1d1d",            # Rojo oscuro
        "📉 VENTA": "#dc2626",                   # Rojo estándar
        "😴 NEUTRAL": "#9ca3af"                  # Gris
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
