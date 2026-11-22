"""Límite de peticiones por origen (control C-13): evita saturar el servicio
(riesgo R-03 y observación del docente de la Fase 2). Ventana de 60 s en memoria."""
import time
from collections import defaultdict, deque

_ventanas: dict = defaultdict(deque)


def reiniciar():
    _ventanas.clear()


def permitir(origen: str, grupo: str, maximo: int) -> bool:
    ahora = time.monotonic()
    v = _ventanas[(origen, grupo)]
    while v and ahora - v[0] > 60:
        v.popleft()
    if len(v) >= maximo:
        return False
    v.append(ahora)
    return True
