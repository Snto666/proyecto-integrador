import pytest
from fastapi.testclient import TestClient
from app import limite, servicio as sv
from app.db import init_db
from app.main import app

CLAVE_SERVICIO = "clave-de-servicio-SOLO-PRUEBAS"
# Contraseñas ficticias de laboratorio (no son reales)
PW = {"admin1": "Lab-Admin-2026-x", "empleado1": "Lab-Emp1-2026-x",
      "ana.lopez": "Lab-Ana-2026-xx", "carlos.m": "Lab-Carlos-2026-x"}


@pytest.fixture()
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "eventos.log"))
    monkeypatch.setenv("SERVICE_KEY", CLAVE_SERVICIO)
    init_db()
    limite.reiniciar()
    sv.crear_usuario("admin1", PW["admin1"], "administrador")
    for n in ("empleado1", "ana.lopez", "carlos.m"):
        sv.crear_usuario(n, PW[n], "empleado")
    c = TestClient(app, headers={"X-Service-Key": CLAVE_SERVICIO})
    c.log = tmp_path / "eventos.log"
    c.db = tmp_path / "t.db"
    return c


def login(c, usuario, clave=None):
    r = c.post("/auth/login", json={"usuario": usuario, "contrasena": clave or PW[usuario]})
    return r


def bearer(token):
    return {"Authorization": f"Bearer {token}"}
