# Tablero de seguimiento (GitHub Projects)

El tablero es la **fuente oficial del estado del proyecto** (ver contrato de comunicación).

## Crear el tablero (una sola vez, ~5 minutos)

1. En GitHub, abrir el repositorio → pestaña **Projects** → **New project** → plantilla **Board**.
2. Nombre: `Proyecto Integrador – Chat Empresarial`.
3. Columnas (campo *Status*): **Por hacer · En progreso · En revisión · Hecho**.
4. Agregar los issues del repositorio al proyecto (**Add item** → buscar por `#`).
5. Cambiar la visibilidad para que los docentes puedan verlo (o agregarlos como colaboradores) y pegar el enlace en el README.

## Crear los issues de las tareas (opcional, automático)

Con la CLI de GitHub (`gh`, ya disponible en Codespaces) autenticada:

```bash
./scripts/crear_tablero.sh
```

Crea las etiquetas y un issue por cada tarea del cronograma (1.1 … 8.2), con su fase, semana y responsable.

## Reglas

- Una tarea = un issue. Las ramas se nombran `feature/<tarea>-<iniciales>`.
- Un pull request cierra el issue (`Closes #N`) y requiere la aprobación de otro integrante.
