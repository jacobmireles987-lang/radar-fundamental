"""
Limitador de tasa compartido por toda la app.

El plan gratuito de Finnhub permite 60 llamadas/minuto. Como ahora varias
piezas del código (cotizaciones, métricas fundamentales, historial de
precios) llaman a la API, centralizamos aquí el control para que la suma
de TODAS las llamadas nunca rebase el límite y dispare errores 429.

Cualquier función que haga un request a Finnhub debe llamar primero a
`limitador_finnhub.esperar()`.
"""
import time
import threading


class RateLimiter:
    """Limitador de ventana deslizante: permite como máximo `max_calls`
    llamadas dentro de cada periodo de `periodo` segundos. Si se alcanza
    el límite, `esperar()` bloquea hasta que vuelva a haber espacio."""

    def __init__(self, max_calls: int = 50, periodo: float = 60.0):
        self.max_calls = max_calls
        self.periodo = periodo
        self._llamadas = []
        self._lock = threading.Lock()

    def esperar(self) -> None:
        with self._lock:
            ahora = time.time()
            self._llamadas = [t for t in self._llamadas if ahora - t < self.periodo]

            if len(self._llamadas) >= self.max_calls:
                espera = self.periodo - (ahora - self._llamadas[0]) + 0.05
                if espera > 0:
                    time.sleep(espera)
                ahora = time.time()
                self._llamadas = [t for t in self._llamadas if ahora - t < self.periodo]

            self._llamadas.append(time.time())


# Dejamos 10 llamadas de margen bajo el límite real de 60/min de Finnhub,
# por si hay imprecisión en el reloj o llamadas concurrentes de varias
# sesiones de usuario sobre la misma app desplegada.
limitador_finnhub = RateLimiter(max_calls=50, periodo=60.0)
