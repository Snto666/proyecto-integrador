"""Pruebas de seguridad contra el servicio EN VIVO por HTTPS (evidencia de la Fase 3).
Requisitos: servicio iniciado con scripts/iniciar_servidor.sh. Ejecutar desde auth-service/:
    python3 -m scripts.evidencias_vivo
Las contraseñas de prueba se generan al azar y NO se imprimen. Guarda resultados_vivo.csv."""
import csv, json, secrets, socket, ssl, sys, time
import httpx
from app.config import cfg
from app.db import init_db
from app.servicio import crear_usuario

BASE = "https://localhost:8443"
CERT = "certs/servidor.pem"
c = cfg()
if not c.service_key:
    sys.exit("Falta SERVICE_KEY en .env")
init_db()
sfx = secrets.token_hex(2)
def pw(): return "Lab-" + secrets.token_urlsafe(12)
U = {n: (f"{n}_{sfx}", pw()) for n in ("adm", "emp", "ana", "bloq")}
crear_usuario(U["adm"][0], U["adm"][1], "administrador", "instalacion-local")  # procedimiento local
H = {"X-Service-Key": c.service_key}
cli = httpx.Client(base_url=BASE, verify=CERT, headers=H, timeout=10)
filas = []

def reg(id_, desc, esperado, obtenido, ok):
    filas.append((id_, desc, esperado, obtenido, "PASA" if ok else "FALLA"))
    print(f"[{'PASA ' if ok else 'FALLA'}] {id_:<7} {desc}\n          esperado: {esperado}\n          obtenido: {obtenido}")

def login(k, clave=None):
    return cli.post("/auth/login", json={"usuario": U[k][0], "contrasena": clave if clave is not None else U[k][1]})
def bearer(t): return {"Authorization": f"Bearer {t}"}

print("=== Pruebas de seguridad en vivo (HTTPS) ===\n")
ta = login("adm").json()["token"]
# PS-18 creación de cuentas solo por el administrador
for k, rol in (("emp", "empleado"), ("ana", "empleado"), ("bloq", "empleado")):
    r = cli.post("/admin/usuarios", json={"nombre": U[k][0], "contrasena": U[k][1], "rol": rol}, headers=bearer(ta))
    assert r.status_code == 201, r.text
r = cli.post("/admin/usuarios", json={"nombre": "intruso", "contrasena": "Lab-Intruso-2026-x"})
reg("PS-18", "Crear cuenta sin sesión (autorregistro)", "401", r.status_code, r.status_code == 401)
r = cli.post("/admin/usuarios", json={"nombre": "corta_" + sfx, "contrasena": "corta"}, headers=bearer(ta))
reg("PS-18b", "Contraseña de menos de 12 caracteres", "400", r.status_code, r.status_code == 400)

# PS-01 / PS-02
r = login("emp"); te = r.json().get("token", "")
reg("PS-01", "Login con credenciales válidas", "200 + sesión con rol y vencimiento", f"{r.status_code}, rol={r.json().get('rol')}", r.status_code == 200 and bool(te))
msgs = set(); cods = set()
for u, p in ((U["emp"][0], "mala-clave-de-prueba"), ("usuario_inexistente", "mala-clave-de-prueba"), ("", "")):
    r = cli.post("/auth/login", json={"usuario": u, "contrasena": p}); cods.add(r.status_code); msgs.add(r.json()["detail"])
reg("PS-02", "Login inválido: clave errónea, usuario inexistente y campos vacíos", "401 y el MISMO mensaje en los 3 casos", f"{sorted(cods)}, mensajes distintos: {len(msgs)} ('{list(msgs)[0]}')", cods == {401} and len(msgs) == 1)

# PS-03 bloqueo
cods = [login("bloq", "mala-clave-de-prueba").status_code for _ in range(5)]
r = login("bloq")
reg("PS-03", "5 fallos seguidos y luego la clave CORRECTA", "5 x 401 y luego 423 'Cuenta bloqueada temporalmente'", f"{cods} y luego {r.status_code} '{r.json()['detail']}'", cods == [401]*5 and r.status_code == 423)

# PS-04 / 05 / 06 autorización
ta2 = login("ana").json()["token"]
r = cli.post("/demo/mensajes", json={"destinatario": U["ana"][0], "contenido": "Reunión a las 15:00"}, headers=bearer(te))
h = cli.get("/demo/historial", params={"con": U["ana"][0]}, headers=bearer(te))
reg("PS-04", "ACCESO PERMITIDO: empleado envía mensaje y consulta su historial", "201 y 1 mensaje propio", f"{r.status_code} y {len(h.json())} mensaje(s)", r.status_code == 201 and len(h.json()) == 1)
cods = [cli.get("/admin/sesiones", headers=bearer(te)).status_code for _ in range(10)]
r = cli.get("/admin/sesiones", headers=bearer(te))
reg("PS-05", "ACCESO DENEGADO: empleado intenta ver sesiones activas (10 intentos)", "403 'Acceso denegado' x10", f"{set(cods)} x{len(cods)}, '{r.json()['detail']}'", set(cods) == {403})
r = cli.get("/demo/historial", params={"con": U["emp"][0], "usuario": U["emp"][0]}, headers=bearer(ta2))
reg("PS-06", "Cliente modificado (ana) pide historial declarando otro usuario", "ignora el dato del cliente; 1 mensaje propio con empleado, no ajenos", f"{r.status_code}, {len(r.json())} mensaje(s) (los suyos con ese usuario)", r.status_code == 200 and len(r.json()) == 1)
tp = login("emp").json()["token"]
# comprobar que una tercera persona (admin) NO ve conversaciones ajenas
r = cli.get("/demo/historial", params={"con": U["ana"][0]}, headers=bearer(ta))
reg("PS-06b", "Tercer usuario (admin) pide el historial emp-ana", "0 mensajes ajenos (el admin tampoco lee conversaciones)", f"{r.status_code}, {len(r.json())} mensaje(s)", r.status_code == 200 and r.json() == [])

# PS-07 / PS-08 sesiones
r = cli.get("/admin/sesiones", headers=bearer(ta))
reg("PS-07", "Admin lista sesiones activas (sin token)", "200, lista con usuario/inicio/origen y sin campo token", f"{r.status_code}, {len(r.json())} sesión(es), 'token' en la respuesta: {'token' in r.text}", r.status_code == 200 and "token" not in r.text)
t0 = time.time()
cli.delete(f"/admin/sesiones/{U['emp'][0]}", headers=bearer(ta))
r = cli.post("/auth/validar", json={"token": te}); dt = time.time() - t0
reg("PS-07b", "Admin cierra la sesión de un empleado", "token rechazado en 5 s o menos", f"{r.status_code} en {dt:.2f} s", r.status_code == 401 and dt <= 5)
tl = login("ana").json()["token"]
cli.post("/auth/logout", json={"token": tl})
cods = {cli.post("/auth/validar", json={"token": tl}).status_code for _ in range(10)}
r = cli.post("/auth/validar", json={"token": "token-inventado-123"})
reg("PS-08", "Sesión cerrada (10 intentos) y token inventado", "401 'Sesión inválida o vencida'", f"{cods} y {r.status_code} '{r.json()['detail']}'", cods == {401} and r.status_code == 401)

# PS-09 TLS
def tls(maxv):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT); ctx.load_verify_locations(CERT)
    ctx.set_ciphers("ALL:@SECLEVEL=0"); ctx.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED; ctx.maximum_version = maxv
    try:
        with socket.create_connection(("localhost", 8443), timeout=5) as s, ctx.wrap_socket(s, server_hostname="localhost") as ss:
            return ss.version()
    except Exception as e:
        return f"RECHAZADA ({type(e).__name__})"
v12 = tls(ssl.TLSVersion.TLSv1_2); v11 = tls(ssl.TLSVersion.TLSv1_1)
try: httpx.get(BASE.replace("https", "http") + "/auth/validar", timeout=5); plano = "ACEPTADA"
except Exception as e: plano = f"RECHAZADA ({type(e).__name__})"
reg("PS-09", "Canal cifrado: TLS 1.2 aceptado; TLS 1.1 y HTTP sin cifrado rechazados", "TLSv1.2/1.3 acepta; TLS 1.1 y texto plano rechazados", f"TLS<=1.2: {v12}; TLS 1.1: {v11}; HTTP plano: {plano}", v12.startswith("TLS") and v11.startswith("RECHAZADA") and plano.startswith("RECHAZADA"))

# PS-11 clave de servicio
r1 = httpx.post(BASE + "/auth/login", json={"usuario": "x", "contrasena": "y"}, verify=CERT)
r2 = httpx.post(BASE + "/auth/login", json={"usuario": "x", "contrasena": "y"}, verify=CERT, headers={"X-Service-Key": "clave-incorrecta"})
reg("PS-11", "Llamar al servicio sin clave de servicio y con clave incorrecta", "401 y 401 'No autorizado'", f"{r1.status_code} y {r2.status_code}", r1.status_code == 401 == r2.status_code)

# PS-12 entradas inválidas
t = login("ana").json()["token"]
malas = [{"destinatario": U["emp"][0], "contenido": ""}, {"destinatario": U["emp"][0], "contenido": "x"*1001}, {"destinatario": U["emp"][0]}, {"contenido": "hola"}]
cods = [cli.post("/demo/mensajes", json=m, headers=bearer(t)).status_code for m in malas]
cods.append(cli.post("/demo/mensajes", content=b"{no es json", headers={**bearer(t), "Content-Type": "application/json"}).status_code)
cods.append(cli.post("/demo/mensajes", content=b"x"*5000, headers={**bearer(t), "Content-Type": "application/json"}).status_code)
vivo = cli.post("/demo/mensajes", json={"destinatario": U["emp"][0], "contenido": "sigo vivo"}, headers=bearer(t)).status_code
reg("PS-12", "6 entradas inválidas (vacía, 1001 car., faltantes, JSON roto, cuerpo grande)", "400 o 413 y el servicio sigue disponible (201)", f"{cods} y luego {vivo}", all(x in (400, 413) for x in cods) and vivo == 201)

# PS-15 registros
log = open(c.log_path, encoding="utf-8").read()
tipos = {json.loads(l)["evento"] for l in log.splitlines()}
secretos = [U[k][1] for k in U] + [te, t, ta]
reg("PS-15", "Registros de eventos sin contraseñas ni tokens", "eventos login_ok, login_fallido, cuenta_bloqueada, acceso_denegado; 0 secretos", f"eventos: {len(tipos)} tipos; secretos hallados: {sum(s in log for s in secretos)}", {"login_ok","login_fallido","cuenta_bloqueada","acceso_denegado"} <= tipos and not any(s in log for s in secretos))

# PS-17 límite de peticiones (al final, para no afectar lo anterior)
estados = [cli.post("/auth/login", json={"usuario": "x", "contrasena": "y"}).status_code for _ in range(c.limite_login + 10)]
reg("PS-17", f"Ráfaga de {len(estados)} logins en menos de 1 minuto (límite {c.limite_login}/min)", "al aparecer 429 'Demasiadas peticiones'", f"primer 429 en la petición n.º {estados.index(429)+1 if 429 in estados else 'ninguno'}", 429 in estados)

with open("resultados_vivo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id", "prueba", "esperado", "obtenido", "resultado"]); w.writerows(filas)
ok = sum(1 for x in filas if x[4] == "PASA")
print(f"\nRESUMEN: {ok} de {len(filas)} pruebas PASAN. Detalle guardado en resultados_vivo.csv")
