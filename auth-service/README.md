# auth-service — Servicio de autenticación (FastAPI)

Parte de seguridad del Chat Empresarial (Proyecto Integrador, Grupo 11). Implementa los
controles de la Fase 2 que se pueden demostrar con el servicio solo.

| Control | Qué hace | Archivo |
|---|---|---|
| C-01 | Solo acepta TLS 1.2 o superior | `scripts/iniciar_servidor.sh` |
| C-02 | Contraseñas con hash Argon2id y sal única | `app/seguridad.py` |
| C-03 | Bloqueo 5 min tras 5 fallos; mismo mensaje y mismo tiempo de respuesta | `app/servicio.py` |
| C-04 | Token aleatorio de 256 bits; solo se guarda su hash; expira a los 15 min sin uso y a las 8 h | `app/servicio.py` |
| C-05 | Rol y propietario se toman de la sesión, nunca del cliente; lo no permitido se deniega | `app/main.py` |
| C-06 | Validación de entradas y errores sin datos internos | `app/main.py` |
| C-07 | Registro de eventos sin contraseñas ni tokens | `app/eventos.py` |
| C-08 | Secretos en `.env` (ignorado por Git) | `.gitignore`, `.env.example` |
| C-09 | Clave de servicio obligatoria (`X-Service-Key`) | `app/main.py` |
| C-13 | Límite de peticiones por origen (nuevo) | `app/limite.py` |

Pendientes (Fase 4): C-10 y C-11 (firewall y administración de red), C-12 (AES de mensajes).

Ejecución paso a paso: ver `GUIA_EJECUCION.md`.
