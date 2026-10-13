# Proyecto Integrador – Tercer Nivel · Chat Empresarial distribuido

> Plataforma empresarial distribuida entre dos sedes que integra **Redes, Desarrollo de Software (Go) y Seguridad Informática**, con validación estadística y análisis socio-tecnológico.
> UIDE · Escuela de Ciencias de la Computación · Ingeniería en Sistemas de Información · Periodo Septiembre 2026 – Enero 2027.

**Estado actual:** Fase 1 (Contexto, planificación y organización) entregada. Las secciones marcadas con se completarán en las fases indicadas.

## Video de presentación (Fase 1)

🎥 **Enlace VIDEO EXPLICATIVO SOLICITADO PARA LA FASE 1:** _https://youtu.be/DPoNVu9Z1W0_ 

## 1. Descripción del proyecto y arquitectura

Una empresa abrió una segunda sede y necesita comunicar a su personal de forma **segura, controlada y medible**. El equipo desarrolla un **Chat Empresarial** cliente-servidor en **Go**, con autenticación mediante un servicio **FastAPI**, desplegado sobre una red de dos sedes con VLAN y OSPF.

- **Aplicación (app-go):** cliente y servidor de chat en Go (structs + composición, interfaces).
- **Autenticación (auth-service):** FastAPI registra usuarios, protege contraseñas con hash y emite la sesión (token). El servidor Go solo la valida.
- **Red (network):** dos sedes con routers OpenWrt (OSPF), VLAN/VLSM sobre 10.10.0.0/16, EtherChannel, RSTP, DHCP, NAT y firewall.  Fases 3–5
- **Investigación (research):** instrumento, datos y análisis estadístico.  Fases 2–6
- **Documentación (docs):** documentos entregables, diagramas y actas.

Diagrama de clases preliminar: [`docs/04_Diagrama_UML_Clases.png`](docs/04_Diagrama_UML_Clases.png).

## 2. Requisitos de software y hardware

| Componente | Requisito |
|---|---|
| Go | 1.22 o superior |
| Python | 3.11 o superior (servicio FastAPI) |
| Git | 2.x |
| Red  | Routers OpenWrt (Raspberry Pi o equivalente autorizado) y switches |

## 3. Instrucciones de instalación y ejecución 

Se documentarán a medida que existan los componentes (Fase 4 y Fase 5). Previsto:

```bash
# Servicio de autenticación
cd auth-service && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Servidor y cliente de chat
cd app-go
go run ./cmd/servidor
go run ./cmd/cliente
```

## 4. Variables de entorno y datos de prueba seguros 

Las credenciales y secretos **nunca** se suben al repositorio. Se usará un archivo `.env` (ignorado por Git) y un archivo `.env.example` con valores ficticios.

## 5. Estructura de carpetas

```text
proyecto-integrador/
├── app-go/           # Aplicación cliente-servidor en Go
│   ├── cmd/          #   servidor/ y cliente/ (puntos de entrada)
│   └── internal/     #   modelo/, autenticacion/ ... (paquetes internos)
├── auth-service/     # Servicio de autenticación FastAPI
│   ├── app/
│   └── tests/
├── network/          # Diseño y configuraciones de red
│   ├── diagrams/
│   ├── configs/
│   └── addressing/
├── research/         # Investigación cuantitativa
│   ├── instruments/
│   ├── data/
│   └── analysis/
├── docs/             # Documentos, diagramas, actas y decisiones
├── LICENSE
└── README.md
```

## 6. Cómo ejecutar las pruebas 

```bash
cd app-go && go test ./...
cd auth-service && pytest
```

## 7. Documentación de la Fase 1

| Entregable | Archivo |
|---|---|
| Documento de contexto y selección del sistema | [`docs/01_Contexto_y_Seleccion_del_Sistema.pdf`](docs/01_Contexto_y_Seleccion_del_Sistema.pdf) |
| Matriz de actores, roles y responsabilidades | [`docs/02_Matriz_Actores_Roles_Responsabilidades.pdf`](docs/02_Matriz_Actores_Roles_Responsabilidades.pdf) |
| Contrato de comunicación del equipo | [`docs/03_Contrato_de_Comunicacion.pdf`](docs/03_Contrato_de_Comunicacion.pdf) |
| Diagrama de clases UML inicial | [`docs/04_Diagrama_UML_Clases.png`](docs/04_Diagrama_UML_Clases.png) |
| Tablero de seguimiento | _https://github.com/users/Snto666/projects/1_  |

## 8. Licencia

Licencia Open Source **MIT** (preliminar; se confirmará en la entrega definitiva). Ver [`LICENSE`](LICENSE).

## 9. Créditos, atribuciones y uso de IA

- **Código propio:** escrito por el equipo.
- **Librerías:** biblioteca estándar de Go y FastAPI (MIT); se listarán versiones y licencias en cada fase.
- **Imágenes y diagramas:** elaborados por el equipo.
- **Asistencia de IA:** se utilizó **Claude (Anthropic)** como apoyo para estructurar y redactar borradores de documentos, proponer el borrador del diagrama UML y la estructura del repositorio. Todo fue revisado y validado por el equipo. Declaración completa en la sección 8 de `docs/01_Contexto_y_Seleccion_del_Sistema.pdf`. Los cambios asistidos se marcan con la etiqueta `asistido-por-ia`.

## 10. Autores y contribuciones

| Integrante | Rol principal | GitHub |
|---|---|---|
| Santiago Yambay | Líder de proyecto, servidor Go, repositorio e integración | [@Snto666](https://github.com/Snto666) |
| Daniel Villareal | Cliente Go, interfaz y red de dos sedes | [@D4n13lV1ll4rr34l](https://github.com/D4n13lV1ll4rr34l) |
| Esteban Trujillo | FastAPI, seguridad, estadística y Tecnología y Sociedad | [@EsTr2007](https://github.com/EsTr2007) |

Las contribuciones individuales se verifican mediante el historial de commits, los pull requests y el tablero de tareas.
