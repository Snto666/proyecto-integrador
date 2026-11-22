"""Base de datos SQLite del servicio de autenticación (almacén de usuarios)."""
import sqlite3
from .config import cfg

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,        -- solo hash Argon2id, nunca la contraseña
  rol TEXT NOT NULL CHECK (rol IN ('empleado','administrador')),
  activo INTEGER NOT NULL DEFAULT 1,
  fallos INTEGER NOT NULL DEFAULT 0,
  bloqueado_hasta REAL,
  creado REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sesiones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token_hash TEXT UNIQUE NOT NULL,    -- solo el hash SHA-256 del token
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
  creada REAL NOT NULL,
  ultima_actividad REAL NOT NULL,
  expira REAL NOT NULL,
  revocada INTEGER NOT NULL DEFAULT 0,
  origen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mensajes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  remitente_id INTEGER NOT NULL REFERENCES usuarios(id),
  destinatario_id INTEGER NOT NULL REFERENCES usuarios(id),
  contenido TEXT NOT NULL,
  enviado REAL NOT NULL
);
"""


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(cfg().db_path)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript(ESQUEMA)
