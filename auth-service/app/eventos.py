"""Registro de eventos de seguridad (control C-07). Guarda fecha, hora, evento,
usuario y origen. NUNCA contraseñas ni tokens."""
import json, os
from datetime import datetime, timezone
from .config import cfg


def evento(tipo: str, usuario: str | None, origen: str, detalle: str = ""):
    ruta = cfg().log_path
    d = os.path.dirname(ruta)
    if d:
        os.makedirs(d, exist_ok=True)
    linea = {
        "fecha_hora": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evento": tipo, "usuario": usuario, "origen": origen, "detalle": detalle,
    }
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
