"""Mecanismos criptográficos: hash de contraseñas (C-02) y tokens de sesión (C-04)."""
import hashlib, re, secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

# Argon2id con sal aleatoria única por contraseña (la sal la genera la librería).
_ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)  # 64 MiB
_HASH_FICTICIO = _ph.hash("contrasena-ficticia-para-igualar-tiempos")
_RE_USUARIO = re.compile(r"^[a-z0-9._-]{3,32}$")


def hashear(clave: str) -> str:
    return _ph.hash(clave)


def verificar(hash_guardado: str, clave: str) -> bool:
    try:
        return _ph.verify(hash_guardado, clave)
    except (VerifyMismatchError, InvalidHashError):
        return False


def verificar_ficticio(clave: str):
    """Para usuarios inexistentes: gasta el mismo tiempo que uno real y así la
    respuesta no delata si la cuenta existe."""
    verificar(_HASH_FICTICIO, clave)


def usuario_valido(nombre: str) -> bool:
    return bool(_RE_USUARIO.match(nombre or ""))


def nuevo_token() -> str:
    return secrets.token_urlsafe(32)  # 256 bits aleatorios


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
