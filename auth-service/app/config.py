"""Configuración leída de variables de entorno o del archivo .env (control C-08:
los secretos viven fuera del código)."""
import os, time
from dataclasses import dataclass
from pathlib import Path


def _cargar_env():
    ruta = Path(".env")
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_cargar_env()


@dataclass
class Config:
    service_key: str
    db_path: str
    log_path: str
    max_intentos: int
    bloqueo_min: int
    inactividad_min: int
    sesion_max_h: int
    limite_login: int
    limite_general: int


def cfg() -> Config:
    g = os.environ.get
    return Config(
        service_key=g("SERVICE_KEY", ""),
        db_path=g("DB_PATH", "auth.db"),
        log_path=g("LOG_PATH", "logs/eventos.log"),
        max_intentos=int(g("MAX_INTENTOS", "5")),
        bloqueo_min=int(g("BLOQUEO_MINUTOS", "5")),
        inactividad_min=int(g("INACTIVIDAD_MINUTOS", "15")),
        sesion_max_h=int(g("SESION_MAX_HORAS", "8")),
        limite_login=int(g("LIMITE_LOGIN_POR_MIN", "20")),
        limite_general=int(g("LIMITE_GENERAL_POR_MIN", "120")),
    )


def ahora() -> float:
    return time.time()
