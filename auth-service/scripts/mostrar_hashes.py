"""Evidencia de protección de credenciales (C-02, C-04): muestra cómo quedan
guardadas las contraseñas y los tokens. Corta los valores para no exponer secretos."""
import sqlite3
from app.config import cfg

con = sqlite3.connect(cfg().db_path)
print("Columnas de la tabla usuarios:", [r[1] for r in con.execute("PRAGMA table_info(usuarios)")])
print("Columnas de la tabla sesiones :", [r[1] for r in con.execute("PRAGMA table_info(sesiones)")])
print("\nUSUARIOS (nombre | rol | password_hash recortado)")
for n, rol, h in con.execute("SELECT nombre, rol, password_hash FROM usuarios"):
    partes = h.split("$")  # ['', 'argon2id', 'v=19', 'm=..,t=..,p=..', sal, hash]
    print(f"  {n:<16}| {rol:<13}| ${partes[1]}${partes[2]}${partes[3]}$<sal {len(partes[4])} car.>${partes[5][:10]}...")
print("\nSESIONES (solo hash SHA-256 del token, recortado)")
for (h,) in con.execute("SELECT token_hash FROM sesiones LIMIT 5"):
    print("  ", h[:16] + "...", f"({len(h)} caracteres hex = 256 bits)")
