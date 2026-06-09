import pandas as pd

def obtener_todos():
    bmv = pd.DataFrame([
        {"Ticker":"AMXL",     "Nombre":"América Móvil",     "Grupo":"🇲🇽 BMV","Precio":9.85, "Cambio %":0.51, "Volumen":45000000,"Beta":0.85,"P/E":12.3,"Mkt Cap":1200000000000,"52w Alto":11.20,"52w Bajo":8.10,"Recomendacion":"buy"},
        {"Ticker":"FEMSAUBD", "Nombre":"FEMSA",             "Grupo":"🇲🇽 BMV","Precio":189.5,"Cambio %":-0.3, "Volumen":3200000, "Beta":0.72,"P/E":18.1,"Mkt Cap":320000000000, "52w Alto":210.0,"52w Bajo":160.0,"Recomendacion":"hold"},
        {"Ticker":"BIMBOA",   "Nombre":"Grupo Bimbo",       "Grupo":"🇲🇽 BMV","Precio":71.20,"Cambio %":1.20, "Volumen":2100000, "Beta":0.61,"P/E":21.4,"Mkt Cap":180000000000, "52w Alto":82.0, "52w Bajo":58.0,"Recomendacion":"buy"},
        {"Ticker":"WALMEX",   "Nombre":"Walmart México",    "Grupo":"🇲🇽 BMV","Precio":58.30,"Cambio %":0.80, "Volumen":8900000, "Beta":0.55,"P/E":25.6,"Mkt Cap":920000000000, "52w Alto":65.0, "52w Bajo":48.0,"Recomendacion":"hold"},
        {"Ticker":"GMEXICOB", "Nombre":"Grupo México",      "Grupo":"🇲🇽 BMV","Precio":112.0,"Cambio %":2.10, "Volumen":5600000, "Beta":1.20,"P/E":9.8, "Mkt Cap":420000000000, "52w Alto":130.0,"52w Bajo":88.0,"Recomendacion":"buy"},
        {"Ticker":"TLEVICPO", "Nombre":"Televisa",          "Grupo":"🇲🇽 BMV","Precio":21.40,"Cambio %-":-1.2,"Volumen":1200000, "Beta":0.95,"P/E":None,"Mkt Cap":35000000000,  "52w Alto":28.0, "52w Bajo":15.0,"Recomendacion":"hold"},
        {"Ticker":"AC",       "Nombre":"Arca Continental",  "Grupo":"🇲🇽 BMV","Precio":155.0,"Cambio %":0.60, "Volumen":980000,  "Beta":0.58,"P/E":19.2,"Mkt Cap":260000000000, "52w Alto":170.0,"52w Bajo":130.0,"Recomendacion":"buy"},
        {"Ticker":"ALSEA",    "Nombre":"Alsea",             "Grupo":"🇲🇽 BMV","Precio":42.10,"Cambio %":-0.5, "Volumen":760000,  "Beta":1.10,"P/E":22.5,"Mkt Cap":45000000000,  "52w Alto":52.0, "52w Bajo":32.0,"Recomendacion":"hold"},
        {"Ticker":"KOFUBL",   "Nombre":"Coca-Cola FEMSA",   "Grupo":"🇲🇽 BMV","Precio":98.50,"Cambio %":1.40, "Volumen":1450000, "Beta":0.65,"P/E":16.8,"Mkt Cap":195000000000, "52w Alto":108.0,"52w Bajo":82.0,"Recomendacion":"buy"},
        {"Ticker":"GCARSOA1", "Nombre":"Grupo Carso",       "Grupo":"🇲🇽 BMV","Precio":88.20,"Cambio %":0.30, "Volumen":620000,  "Beta":0.80,"P/E":14.1,"Mkt Cap":120000000000, "52w Alto":98.0, "52w Bajo":72.0,"Recomendacion":"hold"},
    ])

    nyse = pd.DataFrame([
        {"Ticker":"AAPL", "Nombre":"Apple Inc",       "Grupo":"🇺🇸 NYSE","Precio":189.50,"Cambio %":0.80, "Volumen":55000000, "Beta":1.20,"P/E":28.5,"Mkt Cap":2900000000000,"52w Alto":199.0,"52w Bajo":164.0,"Recomendacion":"buy"},
        {"Ticker":"NVDA", "Nombre":"NVIDIA Corp",     "Grupo":"🇺🇸 NYSE","Precio":875.40,"Cambio %":2.30, "Volumen":42000000, "Beta":1.65,"P/E":65.2,"Mkt Cap":2150000000000,"52w Alto":974.0,"52w Bajo":402.0,"Recomendacion":"buy"},
        {"Ticker":"MSFT", "Nombre":"Microsoft",       "Grupo":"🇺🇸 NYSE","Precio":415.20,"Cambio %":0.50, "Volumen":22000000, "Beta":0.90,"P/E":35.1,"Mkt Cap":3080000000000,"52w Alto":430.0,"52w Bajo":310.0,"Recomendacion":"buy"},
        {"Ticker":"TSLA", "Nombre":"Tesla Inc",       "Grupo":"🇺🇸 NYSE","Precio":175.30,"Cambio %":-1.2, "Volumen":98000000, "Beta":2.10,"P/E":45.8,"Mkt Cap":558000000000, "52w Alto":271.0,"52w Bajo":138.0,"Recomendacion":"hold"},
        {"Ticker":"GOOGL","Nombre":"Alphabet",        "Grupo":"🇺🇸 NYSE","Precio":165.80,"Cambio %":1.10, "Volumen":25000000, "Beta":1.05,"P/E":23.4,"Mkt Cap":2040000000000,"52w Alto":179.0,"52w Bajo":120.0,"Recomendacion":"buy"},
        {"Ticker":"AMZN", "Nombre":"Amazon",          "Grupo":"🇺🇸 NYSE","Precio":182.40,"Cambio %":0.90, "Volumen":35000000, "Beta":1.15,"P/E":42.1,"Mkt Cap":1890000000000,"52w Alto":192.0,"52w Bajo":118.0,"Recomendacion":"buy"},
        {"Ticker":"META", "Nombre":"Meta Platforms",  "Grupo":"🇺🇸 NYSE","Precio":490.20,"Cambio %":1.50, "Volumen":18000000, "Beta":1.25,"P/E":24.8,"Mkt Cap":1250000000000,"52w Alto":531.0,"52w Bajo":274.0,"Recomendacion":"buy"},
        {"Ticker":"JPM",  "Nombre":"JPMorgan Chase",  "Grupo":"🇺🇸 NYSE","Precio":198.50,"Cambio %":0.40, "Volumen":12000000, "Beta":1.10,"P/E":11.2,"Mkt Cap":572000000000, "52w Alto":210.0,"52w Bajo":135.0,"Recomendacion":"buy"},
        {"Ticker":"V",    "Nombre":"Visa Inc",        "Grupo":"🇺🇸 NYSE","Precio":275.30,"Cambio %":0.60, "Volumen":8500000,  "Beta":0.95,"P/E":31.5,"Mkt Cap":565000000000, "52w Alto":290.0,"52w Bajo":220.0,"Recomendacion":"buy"},
        {"Ticker":"UNH",  "Nombre":"UnitedHealth",    "Grupo":"🇺🇸 NYSE","Precio":520.80,"Cambio %":-0.3, "Volumen":4200000,  "Beta":0.70,"P/E":21.8,"Mkt Cap":480000000000, "52w Alto":558.0,"52w Bajo":430.0,"Recomendacion":"hold"},
    ])

    penny = pd.DataFrame([
        {"Ticker":"SNDL","Nombre":"SNDL Inc",        "Grupo":"💰 Penny","Precio":1.85, "Cambio %":3.50, "Volumen":28000000,"Beta":2.80,"P/E":None,"Mkt Cap":420000000,  "52w Alto":3.20, "52w Bajo":1.20,"Recomendacion":"hold"},
        {"Ticker":"CLOV","Nombre":"Clover Health",   "Grupo":"💰 Penny","Precio":0.92, "Cambio %":-2.1, "Volumen":15000000,"Beta":2.10,"P/E":None,"Mkt Cap":280000000,  "52w Alto":2.10, "52w Bajo":0.65,"Recomendacion":"sell"},
        {"Ticker":"GRAB","Nombre":"Grab Holdings",   "Grupo":"💰 Penny","Precio":3.45, "Cambio %":1.80, "Volumen":22000000,"Beta":1.90,"P/E":None,"Mkt Cap":13000000000,"52w Alto":4.80, "52w Bajo":2.80,"Recomendacion":"buy"},
        {"Ticker":"NKLA","Nombre":"Nikola Corp",     "Grupo":"💰 Penny","Precio":0.45, "Cambio %":-5.2, "Volumen":45000000,"Beta":3.20,"P/E":None,"Mkt Cap":180000000,  "52w Alto":1.80, "52w Bajo":0.30,"Recomendacion":"sell"},
        {"Ticker":"HIMS","Nombre":"Hims & Hers",     "Grupo":"💰 Penny","Precio":4.20, "Cambio %":6.80, "Volumen":18000000,"Beta":2.50,"P/E":None,"Mkt Cap":1200000000, "52w Alto":8.90, "52w Bajo":3.10,"Recomendacion":"buy"},
        {"Ticker":"OPEN","Nombre":"Opendoor Tech",   "Grupo":"💰 Penny","Precio":2.10, "Cambio %":2.40, "Volumen":12000000,"Beta":2.80,"P/E":None,"Mkt Cap":1400000000, "52w Alto":4.20, "52w Bajo":1.50,"Recomendacion":"hold"},
        {"Ticker":"SOFI","Nombre":"SoFi Technologies","Grupo":"💰 Penny","Precio":6.85,"Cambio %":1.20, "Volumen":35000000,"Beta":2.20,"P/E":None,"Mkt Cap":6800000000, "52w Alto":10.50,"52w Bajo":5.80,"Recomendacion":"buy"},
        {"Ticker":"WKHS","Nombre":"Workhorse Group", "Grupo":"💰 Penny","Precio":0.38, "Cambio %":-8.5, "Volumen":8900000, "Beta":3.50,"P/E":None,"Mkt Cap":42000000,   "52w Alto":1.20, "52w Bajo":0.22,"Recomendacion":"sell"},
        {"Ticker":"EXPR","Nombre":"Express Inc",     "Grupo":"💰 Penny","Precio":1.15, "Cambio %":4.50, "Volumen":9800000, "Beta":2.60,"P/E":None,"Mkt Cap":95000000,   "52w Alto":3.40, "52w Bajo":0.80,"Recomendacion":"hold"},
        {"Ticker":"BIRD","Nombre":"Allbirds Inc",    "Grupo":"💰 Penny","Precio":0.72, "Cambio %":-3.8, "Volumen":4200000, "Beta":1.80,"P/E":None,"Mkt Cap":88000000,   "52w Alto":1.90, "52w Bajo":0.50,"Recomendacion":"sell"},
    ])

    high_beta = pd.DataFrame([
        {"Ticker":"RIOT","Nombre":"Riot Platforms",  "Grupo":"⚡ Beta","Precio":8.50, "Cambio %":5.20, "Volumen":32000000,"Beta":3.80,"P/E":None,"Mkt Cap":1800000000, "52w Alto":18.50,"52w Bajo":6.20,"Recomendacion":"hold"},
        {"Ticker":"MARA","Nombre":"Marathon Digital", "Grupo":"⚡ Beta","Precio":16.20,"Cambio %":6.80, "Volumen":28000000,"Beta":3.50,"P/E":None,"Mkt Cap":3200000000, "52w Alto":32.00,"52w Bajo":10.50,"Recomendacion":"hold"},
        {"Ticker":"COIN","Nombre":"Coinbase Global",  "Grupo":"⚡ Beta","Precio":198.40,"Cambio %":3.20,"Volumen":15000000,"Beta":3.20,"P/E":28.5,"Mkt Cap":48000000000,"52w Alto":280.0,"52w Bajo":115.0,"Recomendacion":"buy"},
        {"Ticker":"PLTR","Nombre":"Palantir Tech",    "Grupo":"⚡ Beta","Precio":22.80,"Cambio %":2.10, "Volumen":45000000,"Beta":2.60,"P/E":None,"Mkt Cap":48000000000,"52w Alto":28.00,"52w Bajo":13.50,"Recomendacion":"hold"},
        {"Ticker":"HOOD","Nombre":"Robinhood",        "Grupo":"⚡ Beta","Precio":12.40,"Cambio %":4.50, "Volumen":22000000,"Beta":2.90,"P/E":None,"Mkt Cap":10800000000,"52w Alto":18.00,"52w Bajo":8.50,"Recomendacion":"buy"},
        {"Ticker":"RKLB","Nombre":"Rocket Lab",       "Grupo":"⚡ Beta","Precio":5.80, "Cambio %":3.80, "Volumen":18000000,"Beta":2.40,"P/E":None,"Mkt Cap":2800000000, "52w Alto":8.50, "52w Bajo":3.20,"Recomendacion":"buy"},
        {"Ticker":"IONQ","Nombre":"IonQ Inc",         "Grupo":"⚡ Beta","Precio":9.20, "Cambio %":7.50, "Volumen":12000000,"Beta":2.80,"P/E":None,"Mkt Cap":2100000000, "52w Alto":14.50,"52w Bajo":5.80,"Recomendacion":"hold"},
        {"Ticker":"MSTR","Nombre":"MicroStrategy",    "Grupo":"⚡ Beta","Precio":1245.0,"Cambio %":4.20,"Volumen":4500000, "Beta":3.10,"P/E":None,"Mkt Cap":22000000000,"52w Alto":1999.0,"52w Bajo":520.0,"Recomendacion":"hold"},
        {"Ticker":"AFRM","Nombre":"Affirm Holdings",  "Grupo":"⚡ Beta","Precio":38.50,"Cambio %":2.80, "Volumen":9800000, "Beta":2.70,"P/E":None,"Mkt Cap":11800000000,"52w Alto":58.00,"52w Bajo":22.00,"Recomendacion":"buy"},
        {"Ticker":"SMCI","Nombre":"Super Micro Comp.", "Grupo":"⚡ Beta","Precio":780.0,"Cambio %":5.60,"Volumen":8200000, "Beta":1.95,"P/E":18.2,"Mkt Cap":45000000000,"52w Alto":1229.0,"52w Bajo":230.0,"Recomendacion":"hold"},
    ])

    crypto = pd.DataFrame([
        {"Ticker":"BTC",  "Nombre":"Bitcoin",      "Grupo":"🪙 Cripto","Precio":67500.0,"Cambio %":2.10, "Volumen":28000000000,"Beta":1.50,"P/E":None,"Mkt Cap":1320000000000,"52w Alto":73800.0,"52w Bajo":25000.0,"Recomendacion":"buy"},
        {"Ticker":"ETH",  "Nombre":"Ethereum",     "Grupo":"🪙 Cripto","Precio":3480.0, "Cambio %":1.80, "Volumen":15000000000,"Beta":1.65,"P/E":None,"Mkt Cap":418000000000, "52w Alto":4090.0, "52w Bajo":1520.0,"Recomendacion":"buy"},
        {"Ticker":"BNB",  "Nombre":"BNB",          "Grupo":"🪙 Cripto","Precio":580.0,  "Cambio %":0.90, "Volumen":1800000000, "Beta":1.40,"P/E":None,"Mkt Cap":84000000000,  "52w Alto":641.0,  "52w Bajo":210.0,"Recomendacion":"hold"},
        {"Ticker":"SOL",  "Nombre":"Solana",       "Grupo":"🪙 Cripto","Precio":145.0,  "Cambio %":3.50, "Volumen":3200000000, "Beta":1.80,"P/E":None,"Mkt Cap":63000000000,  "52w Alto":210.0,  "52w Bajo":18.0, "Recomendacion":"buy"},
        {"Ticker":"XRP",  "Nombre":"XRP",          "Grupo":"🪙 Cripto","Precio":0.52,   "Cambio %":1.20, "Volumen":2100000000, "Beta":1.60,"P/E":None,"Mkt Cap":28000000000,  "52w Alto":0.92,   "52w Bajo":0.32, "Recomendacion":"hold"},
        {"Ticker":"ADA",  "Nombre":"Cardano",      "Grupo":"🪙 Cripto","Precio":0.48,   "Cambio %":2.80, "Volumen":980000000,  "Beta":1.75,"P/E":None,"Mkt Cap":17000000000,  "52w Alto":0.78,   "52w Bajo":0.24, "Recomendacion":"hold"},
        {"Ticker":"DOGE", "Nombre":"Dogecoin",     "Grupo":"🪙 Cripto","Precio":0.15,   "Cambio %":4.20, "Volumen":1800000000, "Beta":2.10,"P/E":None,"Mkt Cap":21000000000,  "52w Alto":0.22,   "52w Bajo":0.06, "Recomendacion":"hold"},
        {"Ticker":"AVAX", "Nombre":"Avalanche",    "Grupo":"🪙 Cripto","Precio":35.80,  "Cambio %":3.10, "Volumen":620000000,  "Beta":1.90,"P/E":None,"Mkt Cap":14500000000,  "52w Alto":58.00,  "52w Bajo":8.80, "Recomendacion":"buy"},
        {"Ticker":"DOT",  "Nombre":"Polkadot",     "Grupo":"🪙 Cripto","Precio":7.20,   "Cambio %":1.50, "Volumen":420000000,  "Beta":1.85,"P/E":None,"Mkt Cap":9800000000,   "52w Alto":11.80,  "52w Bajo":3.50, "Recomendacion":"hold"},
        {"Ticker":"MATIC","Nombre":"Polygon",      "Grupo":"🪙 Cripto","Precio":0.72,   "Cambio %":2.40, "Volumen":580000000,  "Beta":1.95,"P/E":None,"Mkt Cap":6800000000,   "52w Alto":1.20,   "52w Bajo":0.38, "Recomendacion":"buy"},
    ])

    return {
        "BMV"       : bmv,
        "NYSE"      : nyse,
        "Penny"     : penny,
        "High Beta" : high_beta,
        "Crypto"    : crypto,
    }
