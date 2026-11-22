#!/bin/sh
# Arranca el servicio solo con TLS 1.2 o superior (C-01). Puerto 8443 para la demo local;
# en la red del proyecto será 10.10.0.195:8000.
exec python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8443 \
  --ssl-keyfile certs/servidor.key --ssl-certfile certs/servidor.pem
