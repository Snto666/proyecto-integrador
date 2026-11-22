"""Lógica de autenticación: cuentas, inicio de sesión, bloqueo y sesiones."""
from .config import cfg, ahora
from .db import conn
from .eventos import evento
from . import seguridad as seg

MSG_CRED = "Credenciales inválidas"
MSG_BLOQ = "Cuenta bloqueada temporalmente"
MSG_SESION = "Sesión inválida o vencida"
MSG_DENEGADO = "Acceso denegado"


class ErrorServicio(Exception):
    def __init__(self, estado: int, mensaje: str):
        self.estado, self.mensaje = estado, mensaje


def crear_usuario(nombre: str, clave: str, rol: str, origen: str = "local") -> dict:
    """Solo un administrador (o el procedimiento local de instalación) crea cuentas."""
    if not seg.usuario_valido(nombre):
        raise ErrorServicio(400, "Nombre de usuario inválido (3 a 32 caracteres: a-z, 0-9, . _ -)")
    if len(clave) < 12:
        raise ErrorServicio(400, "La contraseña debe tener al menos 12 caracteres")
    if len(clave) > 128:
        raise ErrorServicio(400, "La contraseña es demasiado larga")
    if rol not in ("empleado", "administrador"):
        raise ErrorServicio(400, "Rol inválido")
    with conn() as c:
        if c.execute("SELECT 1 FROM usuarios WHERE nombre=?", (nombre,)).fetchone():
            raise ErrorServicio(409, "El usuario ya existe")
        cur = c.execute(
            "INSERT INTO usuarios(nombre,password_hash,rol,creado) VALUES (?,?,?,?)",
            (nombre, seg.hashear(clave), rol, ahora()))
        uid = cur.lastrowid
    evento("usuario_creado", nombre, origen, f"rol={rol}")
    return {"usuarioID": uid, "nombreUsuario": nombre, "rol": rol}


def iniciar_sesion(nombre: str, clave: str, origen: str) -> dict:
    c_ = cfg()
    now = ahora()
    with conn() as c:
        fila = None
        if seg.usuario_valido(nombre) and clave:
            fila = c.execute("SELECT * FROM usuarios WHERE nombre=?", (nombre,)).fetchone()
        usuario_log = nombre if seg.usuario_valido(nombre) else "(formato inválido o vacío)"

        if fila is None or not fila["activo"]:
            seg.verificar_ficticio(clave or "x")  # igualar tiempos
            evento("login_fallido", usuario_log, origen, "cuenta inexistente o datos vacíos")
            raise ErrorServicio(401, MSG_CRED)

        if fila["bloqueado_hasta"] and fila["bloqueado_hasta"] > now:
            evento("login_bloqueado", nombre, origen, "intento durante el bloqueo")
            raise ErrorServicio(423, MSG_BLOQ)

        if not seg.verificar(fila["password_hash"], clave):
            fallos = fila["fallos"] + 1
            if fallos >= c_.max_intentos:
                c.execute("UPDATE usuarios SET fallos=0, bloqueado_hasta=? WHERE id=?",
                          (now + c_.bloqueo_min * 60, fila["id"]))
                evento("cuenta_bloqueada", nombre, origen,
                       f"{c_.max_intentos} fallos seguidos; bloqueo {c_.bloqueo_min} min")
            else:
                c.execute("UPDATE usuarios SET fallos=? WHERE id=?", (fallos, fila["id"]))
            c.commit()  # guardar el contador ANTES de lanzar el error (si no, se revierte)
            evento("login_fallido", nombre, origen, f"fallo {fallos}")
            raise ErrorServicio(401, MSG_CRED)

        c.execute("UPDATE usuarios SET fallos=0, bloqueado_hasta=NULL WHERE id=?", (fila["id"],))
        token = seg.nuevo_token()
        expira = now + c_.sesion_max_h * 3600
        c.execute(
            "INSERT INTO sesiones(token_hash,usuario_id,creada,ultima_actividad,expira,origen)"
            " VALUES (?,?,?,?,?,?)",
            (seg.hash_token(token), fila["id"], now, now, expira, origen))
    evento("login_ok", nombre, origen)
    return {"token": token, "usuarioID": fila["id"], "nombreUsuario": nombre,
            "rol": fila["rol"], "expiraEn": expira}


def validar_token(token: str, origen: str) -> dict:
    c_ = cfg()
    now = ahora()
    with conn() as c:
        fila = None
        if token:
            fila = c.execute(
                "SELECT s.*, u.nombre, u.rol, u.activo FROM sesiones s "
                "JOIN usuarios u ON u.id=s.usuario_id WHERE s.token_hash=?",
                (seg.hash_token(token),)).fetchone()
        vigente = (fila is not None and not fila["revocada"] and fila["activo"]
                   and now < fila["expira"]
                   and now - fila["ultima_actividad"] <= c_.inactividad_min * 60)
        if not vigente:
            evento("sesion_invalida", fila["nombre"] if fila else None, origen)
            raise ErrorServicio(401, MSG_SESION)
        c.execute("UPDATE sesiones SET ultima_actividad=? WHERE id=?", (now, fila["id"]))
    return {"usuarioID": fila["usuario_id"], "nombreUsuario": fila["nombre"],
            "rol": fila["rol"], "expiraEn": fila["expira"]}


def cerrar_sesion(token: str, origen: str):
    info = validar_token(token, origen)
    with conn() as c:
        c.execute("UPDATE sesiones SET revocada=1 WHERE token_hash=?", (seg.hash_token(token),))
    evento("logout", info["nombreUsuario"], origen)


def sesiones_activas() -> list:
    now = ahora()
    lim = cfg().inactividad_min * 60
    with conn() as c:
        filas = c.execute(
            "SELECT u.nombre, s.creada, s.origen FROM sesiones s JOIN usuarios u ON u.id=s.usuario_id "
            "WHERE s.revocada=0 AND s.expira>? AND ?-s.ultima_actividad<=? ORDER BY s.creada",
            (now, now, lim)).fetchall()
    # No se incluye el token ni su hash.
    return [{"usuario": f["nombre"], "inicio": f["creada"], "origen": f["origen"]} for f in filas]


def revocar_sesiones_de(usuario: str, admin: str, origen: str):
    with conn() as c:
        u = c.execute("SELECT id FROM usuarios WHERE nombre=?", (usuario,)).fetchone()
        n = 0
        if u:
            n = c.execute("UPDATE sesiones SET revocada=1 WHERE usuario_id=? AND revocada=0",
                          (u["id"],)).rowcount
    if n == 0:
        raise ErrorServicio(404, "El usuario no tiene sesión activa")
    evento("sesion_revocada_admin", usuario, origen, f"por {admin}")


def buscar_usuario(nombre: str) -> dict:
    with conn() as c:
        u = c.execute("SELECT id, nombre FROM usuarios WHERE nombre=? AND activo=1", (nombre,)).fetchone()
    if not u:
        raise ErrorServicio(404, "El usuario no existe")
    return {"usuarioID": u["id"], "nombreUsuario": u["nombre"]}
