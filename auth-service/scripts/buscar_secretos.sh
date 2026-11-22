#!/bin/sh
# Búsqueda sencilla de secretos en los archivos versionados y en el historial (C-08, PS-13).
# Ejecutar desde la raíz del repositorio.
PATRON='(SERVICE_KEY|ADMIN_PASSWORD|password|contrasena|secret|BEGIN (RSA |EC )?PRIVATE KEY)[[:space:]]*[=:][[:space:]]*["'"'"']?[A-Za-z0-9+/_-]{8,}'
echo "== Archivos versionados =="
git ls-files | grep -v -E '\.env\.example$|tests/|scripts/|\.md$|requirements' | xargs -r grep -n -i -E "$PATRON" || echo "0 hallazgos"
echo "== Historial de Git =="
git log -p --all 2>/dev/null | grep -i -E "^\+.*$PATRON" | grep -v -E 'CAMBIAR|ficticio' || echo "0 hallazgos"
echo "== Archivos sensibles versionados (.env, claves, .db) =="
git ls-files | grep -E '(^|/)\.env$|\.key$|\.pem$|\.db$' || echo "0 archivos sensibles en el repositorio"
