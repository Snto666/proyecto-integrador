"""Pruebas de seguridad de la Fase 3. Cada prueba lleva el código PS-xx del plan
de la Fase 2. Ejecutar:  pytest -v"""
import json, sqlite3, time
from app.main import app
from fastapi.testclient import TestClient
from .conftest import PW, CLAVE_SERVICIO, login, bearer


# ---- Autenticación (C-03, C-04) ----
def test_PS01_login_valido_emite_sesion(api):
    r = login(api, "empleado1")
    assert r.status_code == 200
    d = r.json()
    assert d["rol"] == "empleado" and d["expiraEn"] > time.time()
    assert len(d["token"]) >= 43  # 256 bits en base64url


def test_PS02_login_invalido_mismo_mensaje(api):
    casos = [("empleado1", "contrasena-incorrecta-1"), ("noexiste", "cualquier-clave-123"),
             ("", ""), ("empleado1", "")]
    for u, p in casos:
        r = api.post("/auth/login", json={"usuario": u, "contrasena": p})
        assert r.status_code == 401 and r.json()["detail"] == "Credenciales inválidas"


def test_PS03_bloqueo_tras_5_fallos(api):
    for _ in range(5):
        assert login(api, "ana.lopez", "mala-contrasena-xx").status_code == 401
    r = login(api, "ana.lopez")  # contraseña CORRECTA durante el bloqueo
    assert r.status_code == 423 and r.json()["detail"] == "Cuenta bloqueada temporalmente"
    # Pasados 5 minutos (se adelanta el reloj en la BD) vuelve a funcionar
    with sqlite3.connect(api.db) as c:
        c.execute("UPDATE usuarios SET bloqueado_hasta=? WHERE nombre='ana.lopez'", (time.time() - 1,))
    assert login(api, "ana.lopez").status_code == 200


def test_PS08_sesion_cerrada_vencida_o_inventada(api):
    t = login(api, "empleado1").json()["token"]
    assert api.post("/auth/validar", json={"token": t}).status_code == 200
    assert api.post("/auth/logout", json={"token": t}).status_code == 204
    for _ in range(10):  # tras cerrar sesión, 10 de 10 rechazadas
        r = api.post("/auth/validar", json={"token": t})
        assert r.status_code == 401 and r.json()["detail"] == "Sesión inválida o vencida"
    assert api.post("/auth/validar", json={"token": "token-inventado-123"}).status_code == 401
    # Inactividad de 15 min: se atrasa la última actividad
    t2 = login(api, "empleado1").json()["token"]
    with sqlite3.connect(api.db) as c:
        c.execute("UPDATE sesiones SET ultima_actividad=ultima_actividad-1000 WHERE revocada=0")
    assert api.post("/auth/validar", json={"token": t2}).status_code == 401


# ---- Autorización (C-05) ----
def test_PS04_acceso_permitido_historial_propio(api):
    t = login(api, "empleado1").json()["token"]
    r = api.post("/demo/mensajes", json={"destinatario": "ana.lopez", "contenido": "Reunión a las 15:00"},
                 headers=bearer(t))
    assert r.status_code == 201
    h = api.get("/demo/historial", params={"con": "ana.lopez"}, headers=bearer(t))
    assert h.status_code == 200 and len(h.json()) == 1 and h.json()[0]["de"] == "empleado1"


def test_PS05_acceso_denegado_funciones_admin(api):
    t = login(api, "empleado1").json()["token"]
    for _ in range(10):
        assert api.get("/admin/sesiones", headers=bearer(t)).status_code == 403
        assert api.delete("/admin/sesiones/ana.lopez", headers=bearer(t)).status_code == 403
    r = api.get("/admin/sesiones", headers=bearer(t))
    assert r.json()["detail"] == "Acceso denegado"
    eventos = [json.loads(l)["evento"] for l in api.log.read_text().splitlines()]
    assert eventos.count("acceso_denegado") >= 20


def test_PS06_cliente_modificado_no_ve_mensajes_ajenos(api):
    te = login(api, "empleado1").json()["token"]
    api.post("/demo/mensajes", json={"destinatario": "ana.lopez", "contenido": "privado"}, headers=bearer(te))
    tc = login(api, "carlos.m").json()["token"]
    # carlos pide la conversación con ana, declarando ser otro usuario por parámetro
    r = api.get("/demo/historial", params={"con": "ana.lopez", "usuario": "empleado1"}, headers=bearer(tc))
    assert r.status_code == 200 and r.json() == []


def test_PS07_admin_lista_y_revoca_sesiones(api):
    ta = login(api, "admin1").json()["token"]
    te = login(api, "empleado1").json()["token"]
    r = api.get("/admin/sesiones", headers=bearer(ta))
    assert r.status_code == 200 and {s["usuario"] for s in r.json()} == {"admin1", "empleado1"}
    assert "token" not in r.text  # nunca se muestra el token
    assert api.delete("/admin/sesiones/empleado1", headers=bearer(ta)).status_code == 204
    assert api.post("/auth/validar", json={"token": te}).status_code == 401
    assert api.delete("/admin/sesiones/empleado1", headers=bearer(ta)).status_code == 404


def test_PS18_sin_autorregistro_y_clave_minima(api):
    r = api.post("/admin/usuarios", json={"nombre": "intruso", "contrasena": "Lab-Intruso-2026", "rol": "administrador"})
    assert r.status_code == 401  # sin sesión
    te = login(api, "empleado1").json()["token"]
    r = api.post("/admin/usuarios", json={"nombre": "intruso", "contrasena": "Lab-Intruso-2026"}, headers=bearer(te))
    assert r.status_code == 403  # empleado no crea cuentas
    ta = login(api, "admin1").json()["token"]
    r = api.post("/admin/usuarios", json={"nombre": "nuevo.u", "contrasena": "corta"}, headers=bearer(ta))
    assert r.status_code == 400
    r = api.post("/admin/usuarios", json={"nombre": "nuevo.u", "contrasena": "Lab-Nuevo-2026-x"}, headers=bearer(ta))
    assert r.status_code == 201


# ---- Protección de credenciales (C-02) y registros (C-07) ----
def test_PS10_contrasenas_con_hash_argon2id(api):
    with sqlite3.connect(api.db) as c:
        filas = c.execute("SELECT nombre, password_hash FROM usuarios").fetchall()
    for _, h in filas:
        assert h.startswith("$argon2id$")
    assert not any(p in h for _, h in filas for p in PW.values())
    # dos usuarios con la MISMA contraseña -> hashes distintos (sal única)
    ta = login(api, "admin1").json()["token"]
    for n in ("gemelo1", "gemelo2"):
        api.post("/admin/usuarios", json={"nombre": n, "contrasena": "Misma-Clave-2026-z"}, headers=bearer(ta))
    with sqlite3.connect(api.db) as c:
        hs = [r[0] for r in c.execute("SELECT password_hash FROM usuarios WHERE nombre LIKE 'gemelo%'")]
    assert len(hs) == 2 and hs[0] != hs[1]


def test_PS15_registros_sin_contrasenas_ni_tokens(api):
    t = login(api, "empleado1").json()["token"]
    login(api, "empleado1", "clave-mala-para-registro")
    api.get("/admin/sesiones", headers=bearer(t))
    texto = api.log.read_text()
    tipos = {json.loads(l)["evento"] for l in texto.splitlines()}
    assert {"login_ok", "login_fallido", "acceso_denegado"} <= tipos
    for secreto in list(PW.values()) + [t, "clave-mala-para-registro"]:
        assert secreto not in texto
    with sqlite3.connect(api.db) as c:  # del token solo se guarda el hash
        assert t not in str(c.execute("SELECT * FROM sesiones").fetchall())


# ---- Comunicación entre servicios (C-09), entradas (C-06), límites (C-13) ----
def test_PS11_clave_de_servicio_obligatoria(api):
    sin = TestClient(app)
    mala = TestClient(app, headers={"X-Service-Key": "clave-incorrecta"})
    for c in (sin, mala):
        r = c.post("/auth/login", json={"usuario": "empleado1", "contrasena": PW["empleado1"]})
        assert r.status_code == 401 and r.json()["detail"] == "No autorizado"
    eventos = [json.loads(l)["evento"] for l in api.log.read_text().splitlines()]
    assert eventos.count("clave_servicio_invalida") == 2


def test_PS12_entradas_invalidas_error_controlado(api):
    t = login(api, "empleado1").json()["token"]
    h = bearer(t)
    casos = [
        ({"destinatario": "ana.lopez", "contenido": ""}, 400),
        ({"destinatario": "ana.lopez", "contenido": "x" * 1001}, 400),
        ({"destinatario": "ana.lopez"}, 400),
        ({"destinatario": "", "contenido": "hola"}, 400),
    ]
    for cuerpo, esperado in casos:
        r = api.post("/demo/mensajes", json=cuerpo, headers=h)
        assert r.status_code == esperado and r.json() == {"detail": "Entrada inválida"}
    r = api.post("/demo/mensajes", content=b"{no es json", headers={**h, "Content-Type": "application/json"})
    assert r.status_code == 400 and "Traceback" not in r.text
    r = api.post("/demo/mensajes", content=b"x" * 5000, headers={**h, "Content-Type": "application/json"})
    assert r.status_code == 413
    assert api.post("/demo/mensajes", json={"destinatario": "ana.lopez", "contenido": "sigo vivo"},
                    headers=h).status_code == 201  # el servicio sigue disponible


def test_PS17_limite_de_peticiones(api, monkeypatch):
    monkeypatch.setenv("LIMITE_LOGIN_POR_MIN", "5")
    estados = [api.post("/auth/login", json={"usuario": "x", "contrasena": "y"}).status_code for _ in range(8)]
    assert estados[:5] == [401] * 5 and estados[5:] == [429] * 3
    r = api.post("/auth/login", json={"usuario": "x", "contrasena": "y"})
    assert r.headers.get("Retry-After") == "60"


def test_PS13_secretos_fuera_del_repositorio():
    import pathlib
    base = pathlib.Path(__file__).resolve().parent.parent
    ign = (base / ".gitignore").read_text()
    assert ".env" in ign and "*.key" in ign and "*.db" in ign
    ejemplo = (base / ".env.example").read_text()
    assert "CAMBIAR" in ejemplo
