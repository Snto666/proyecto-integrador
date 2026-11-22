#!/bin/sh
# Genera un certificado AUTOFIRMADO de laboratorio (control C-01). No se sube al repositorio.
mkdir -p certs
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout certs/servidor.key -out certs/servidor.pem \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null
echo "Certificado de laboratorio creado en certs/ (válido 30 días)"
