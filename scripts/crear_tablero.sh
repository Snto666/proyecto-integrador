#!/usr/bin/env bash
# Crea etiquetas e issues de las tareas del cronograma. Requiere `gh auth login`.
# Ejecutar UNA sola vez, dentro del repositorio ya subido a GitHub.
set -euo pipefail

for l in tarea "Fase 1" "Fase 2" "Fase 3" "Fase 4" "Fase 5" "Fase 6" "Fase 7" "Fase 8" asistido-por-ia; do
  gh label create "$l" --force >/dev/null
done

crear() { # codigo titulo responsable fase semanas
  gh issue create --title "[$1] $2" --label "tarea" --label "$4" \
    --body "**Tarea:** $1 – $2\n**Fase:** $4 · **Semanas:** $5\n**Responsable:** $3\n\n### Criterios de hecho\n- [ ] Entregable subido a la rama correspondiente\n- [ ] Revisado por otro integrante"
}

crear "1.1" "Definir problema y seleccionar el sistema" "Todo el equipo" "Fase 1" "1"
crear "1.2" "Matriz de actores/roles y contrato de comunicación" "Todo el equipo" "Fase 1" "1-2"
crear "1.3" "Repositorio Git, README, licencia y tablero" "Santiago" "Fase 1" "1"
crear "1.4" "Diagrama UML de clases inicial" "Santiago" "Fase 1" "2"
crear "1.5" "Video de presentación y reparto de responsabilidades" "Todo el equipo" "Fase 1" "2"
crear "2.1" "Especificación de requisitos con criterios de aceptación" "Santiago" "Fase 2" "3-4"
crear "2.2" "Casos de uso y flujos principales/alternativos" "Daniel" "Fase 2" "4-5"
crear "2.3" "Propuesta de investigación e instrumento preliminar" "Esteban" "Fase 2" "3-5"
crear "2.4" "Matriz de riesgos, privacidad y consideraciones éticas" "Esteban" "Fase 2" "4-5"
crear "2.5" "Dimensionamiento preliminar de VLAN y direccionamiento" "Daniel" "Fase 2" "4-5"
crear "3.1" "Arquitectura integral y plan VLSM/VLAN" "Daniel" "Fase 3" "6-7"
crear "3.2" "Diseño Go: componentes, clases y secuencia" "Santiago" "Fase 3" "6-7"
crear "3.3" "Modelo de datos y flujo de autenticación (FastAPI)" "Esteban" "Fase 3" "6-7"
crear "3.4" "Plan de pruebas y plan de análisis estadístico" "Esteban" "Fase 3" "7"
crear "3.5" "Prototipo visual de la interfaz" "Daniel" "Fase 3" "7"
crear "4.1" "Servidor Go: conexiones concurrentes y mensajes" "Santiago" "Fase 4" "8-10"
crear "4.2" "Cliente Go y validaciones" "Daniel" "Fase 4" "8-10"
crear "4.3" "FastAPI: registro, inicio de sesión y token" "Esteban" "Fase 4" "8-9"
crear "4.4" "Red: switches, VLAN, trunk, EtherChannel, RSTP y OpenWrt" "Daniel" "Fase 4" "8-10"
crear "4.5" "Prueba piloto del instrumento estadístico" "Esteban" "Fase 4" "9-10"
crear "4.6" "Bitácora de punto crítico y video de avance" "Todo el equipo" "Fase 4" "10"
crear "5.1" "Integración Go <-> FastAPI" "Santiago" "Fase 5" "11"
crear "5.2" "Despliegue en sedes: OSPF, NAT, DHCP y firewall" "Daniel" "Fase 5" "11-12"
crear "5.3" "Pruebas de integración y métricas preliminares" "Todo el equipo" "Fase 5" "12"
crear "5.4" "Backups, matriz de conectividad y evidencias" "Daniel" "Fase 5" "12"
crear "6.1" "Pruebas funcionales, de seguridad y de conectividad" "Santiago" "Fase 6" "13-14"
crear "6.2" "Análisis estadístico e informe" "Esteban" "Fase 6" "13-14"
crear "6.3" "Análisis socio-tecnológico y recomendaciones" "Esteban" "Fase 6" "13-14"
crear "6.4" "Matriz de cumplimiento, versión candidata y video" "Todo el equipo" "Fase 6" "14"
crear "7.1" "Ensayo, presentación y defensa final" "Todo el equipo" "Fase 7" "15"
crear "8.1" "Correcciones y entrega definitiva" "Todo el equipo" "Fase 8" "16"
crear "8.2" "Retrospectiva, autoevaluación y coevaluación" "Todo el equipo" "Fase 8" "16"
echo "Listo: issues creados. Agréguelos a su GitHub Project (ver docs/tablero.md)."
