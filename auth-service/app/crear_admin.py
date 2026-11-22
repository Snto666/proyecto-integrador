"""Procedimiento local de instalación: crea la primera cuenta de administrador.
Uso:  python -m app.crear_admin admin1
La contraseña se pide por teclado (no se muestra) o se toma de la variable
ADMIN_PASSWORD. Nunca se guarda en el repositorio."""
import getpass, os, sys
from .db import init_db
from .servicio import crear_usuario, ErrorServicio

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python -m app.crear_admin <nombre_usuario>")
    init_db()
    clave = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Contraseña del administrador (mín. 12): ")
    try:
        print(crear_usuario(sys.argv[1], clave, "administrador", "instalacion-local"))
    except ErrorServicio as e:
        sys.exit(f"Error: {e.mensaje}")
