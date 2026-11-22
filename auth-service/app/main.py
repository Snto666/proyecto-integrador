"""Servicio de autenticación FastAPI del Chat Empresarial (Fase 3 de Seguridad).
Contrato alineado con la sección 2.4 del documento de POO Fase 3."""
import hmac, os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from . import limite, servicio as sv
from .config import cfg, ahora
from .db import conn, init_db
from .eventos import evento


def origen_de(request: Request) -> str:
    return request.client.host if request.client else "desconocido"


@asynccontextmanager
async def ciclo(app):
    if not cfg().service_key:
        raise RuntimeError("Falta SERVICE_KEY (variable de entorno o archivo .env)")
    init_db()
    yield


def exigir_clave_servicio(request: Request, x_service_key: str | None = Header(default=None)):
    """C-09 / RF-SEC-11: solo el servidor de chat, con la clave de servicio, puede llamar."""
    esperada = cfg().service_key
    if not x_service_key or not hmac.compare_digest(x_service_key.encode(), esperada.encode()):
        evento("clave_servicio_invalida", None, origen_de(request), request.url.path)
        raise sv.ErrorServicio(401, "No autorizado")


app = FastAPI(title="Servicio de autenticación - Chat Empresarial", lifespan=ciclo,
              dependencies=[Depends(exigir_clave_servicio)], docs_url=None, redoc_url=None)


# ---------- Manejo de errores: mensajes controlados, sin datos internos (C-06) ----------
@app.exception_handler(sv.ErrorServicio)
async def _err_servicio(request, exc: sv.ErrorServicio):
    return JSONResponse({"detail": exc.mensaje}, status_code=exc.estado)


@app.exception_handler(RequestValidationError)
async def _err_validacion(request, exc):
    evento("entrada_invalida", None, origen_de(request), request.url.path)
    return JSONResponse({"detail": "Entrada inválida"}, status_code=400)


# ---------- Límite de peticiones y tamaño (C-13, C-06) ----------
@app.middleware("http")
async def limites(request: Request, call_next):
    c = cfg()
    origen = origen_de(request)
    es_login = request.url.path == "/auth/login"
    grupo, maximo = ("login", c.limite_login) if es_login else ("general", c.limite_general)
    if not limite.permitir(origen, grupo, maximo):
        evento("limite_peticiones", None, origen, f"{request.url.path} ({grupo})")
        return JSONResponse({"detail": "Demasiadas peticiones. Intente más tarde."},
                            status_code=429, headers={"Retry-After": "60"})
    tam = request.headers.get("content-length")
    if tam and tam.isdigit() and int(tam) > 4096:
        evento("entrada_invalida", None, origen, "cuerpo demasiado grande")
        return JSONResponse({"detail": "Entrada inválida"}, status_code=413)
    return await call_next(request)


# ---------- Modelos de entrada ----------
class LoginIn(BaseModel):
    usuario: str = Field(default="", max_length=128)
    contrasena: str = Field(default="", max_length=128)


class TokenIn(BaseModel):
    token: str = Field(min_length=1, max_length=256)


class UsuarioIn(BaseModel):
    nombre: str = Field(max_length=64)
    contrasena: str = Field(max_length=256)
    rol: str = Field(default="empleado", max_length=20)


class MensajeIn(BaseModel):
    destinatario: str = Field(min_length=1, max_length=64)
    contenido: str = Field(min_length=1, max_length=1000)


# ---------- Dependencias de sesión y autorización (C-05) ----------
def sesion_actual(request: Request, authorization: str | None = Header(default=None)) -> dict:
    token = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    return sv.validar_token(token, origen_de(request))


def solo_admin(request: Request, s: dict = Depends(sesion_actual)) -> dict:
    if s["rol"] != "administrador":
        evento("acceso_denegado", s["nombreUsuario"], origen_de(request), request.url.path)
        raise sv.ErrorServicio(403, sv.MSG_DENEGADO)
    return s


# ---------- Contrato servidor Go <-> FastAPI ----------
@app.post("/auth/login")
def login(datos: LoginIn, request: Request):
    return sv.iniciar_sesion(datos.usuario, datos.contrasena, origen_de(request))


@app.post("/auth/validar")
def validar(datos: TokenIn, request: Request):
    return sv.validar_token(datos.token, origen_de(request))


@app.post("/auth/logout", status_code=204)
def logout(datos: TokenIn, request: Request):
    sv.cerrar_sesion(datos.token, origen_de(request))
    return Response(status_code=204)


@app.get("/auth/usuarios/{nombre}")
def buscar(nombre: str, s: dict = Depends(sesion_actual)):
    return sv.buscar_usuario(nombre)


# ---------- Funciones de administración (solo rol administrador) ----------
@app.post("/admin/usuarios", status_code=201)
def crear(datos: UsuarioIn, request: Request, admin: dict = Depends(solo_admin)):
    return sv.crear_usuario(datos.nombre, datos.contrasena, datos.rol, origen_de(request))


@app.get("/admin/sesiones")
def sesiones(admin: dict = Depends(solo_admin)):
    return sv.sesiones_activas()


@app.delete("/admin/sesiones/{usuario}", status_code=204)
def cerrar_de(usuario: str, request: Request, admin: dict = Depends(solo_admin)):
    sv.revocar_sesiones_de(usuario, admin["nombreUsuario"], origen_de(request))
    return Response(status_code=204)


# ---------- Recursos protegidos de demostración (simulan lo que hará el chat) ----------
@app.post("/demo/mensajes", status_code=201)
def enviar(datos: MensajeIn, s: dict = Depends(sesion_actual)):
    dest = sv.buscar_usuario(datos.destinatario)  # 404 si no existe
    with conn() as c:  # remitente SIEMPRE tomado de la sesión, no del cliente
        c.execute("INSERT INTO mensajes(remitente_id,destinatario_id,contenido,enviado) VALUES (?,?,?,?)",
                  (s["usuarioID"], dest["usuarioID"], datos.contenido, ahora()))
    return {"detail": "Mensaje enviado"}


@app.get("/demo/historial")
def historial(con: str, s: dict = Depends(sesion_actual)):
    otro = sv.buscar_usuario(con)
    me = s["usuarioID"]  # propietario = usuario de la sesión; se ignora cualquier otro dato
    with conn() as c:
        filas = c.execute(
            "SELECT m.contenido, m.enviado, ur.nombre AS de, ud.nombre AS para FROM mensajes m "
            "JOIN usuarios ur ON ur.id=m.remitente_id JOIN usuarios ud ON ud.id=m.destinatario_id "
            "WHERE (m.remitente_id=? AND m.destinatario_id=?) OR (m.remitente_id=? AND m.destinatario_id=?) "
            "ORDER BY m.enviado DESC LIMIT 50", (me, otro["usuarioID"], otro["usuarioID"], me)).fetchall()
    return [dict(f) for f in reversed(filas)]
