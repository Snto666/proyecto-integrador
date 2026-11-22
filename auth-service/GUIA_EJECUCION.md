# Guía de ejecución y captura de evidencias (Fase 3 – Seguridad)

Funciona igual en GitHub Codespaces, VS Code o GoLand (terminal integrada). Python 3.10 o superior.
Todos los comandos se ejecutan dentro de la carpeta `auth-service/`.

## A. Preparación (una sola vez)
```bash
cd auth-service
python3 -m venv .venv && . .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
Edite `.env` y cambie SERVICE_KEY por una clave larga inventada (no la comparta ni la suba a Git):
```bash
python3 -c "import secrets;print(secrets.token_urlsafe(32))"   # copie el resultado en SERVICE_KEY=
sh scripts/generar_certificado.sh                               # certificado de laboratorio (C-01)
```

## B. Evidencia 1 — pruebas automáticas (captura la terminal completa)
```bash
python3 -m pytest -v
```
Debe terminar con `15 passed`.

## C. Evidencia 2 — servicio en vivo por HTTPS
Terminal 1 (déjela abierta, es el servidor):
```bash
sh scripts/iniciar_servidor.sh
```
Terminal 2 (mismo entorno virtual: `. .venv/bin/activate`):
```bash
python3 -W ignore -m scripts.evidencias_vivo      # CAPTURA: la salida completa (17 pruebas)
python3 -W ignore -m scripts.mostrar_hashes       # CAPTURA: cómo se guardan contraseñas y tokens
tail -n 15 logs/eventos.log                       # CAPTURA: registros de eventos
```
Genera además `resultados_vivo.csv` (envíemelo junto con las capturas).

## D. Evidencia 3 — secretos y Git
```bash
cd ..                                  # raíz del repositorio
sh auth-service/scripts/buscar_secretos.sh
git status                             # CAPTURA: .env, certs/ y *.db NO aparecen
```

## E. Qué me envían para armar el informe (Word)
1. Texto de cada salida (copiar y pegar) o las capturas: B, C (las 3 salidas) y D.
2. `resultados_vivo.csv`.
3. El enlace del repositorio con `auth-service/` subido.
4. Quién ejecutó cada parte (para la tabla de contribuciones).
Si algo falla, péguenme el error tal cual.

## Reglas
- No suban `.env`, `certs/`, `*.db` ni `logs/` (ya están en `.gitignore`).
- Las contraseñas de prueba se generan al azar y no se imprimen.
