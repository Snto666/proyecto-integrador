# app-go – Chat Empresarial (Go)

Aplicación cliente-servidor del chat. Cada «clase» es un `struct` con métodos; **no se usa herencia** (se emplea composición) y el polimorfismo se logra con interfaces.

```text
cmd/servidor      # punto de entrada del servidor        (Fase 4)
cmd/cliente       # punto de entrada del cliente         (Fase 4)
internal/modelo   # Usuario, Mensaje, Sesion             (esqueleto Fase 1)
internal/autenticacion  # interface Autenticador         (esqueleto Fase 1)
```

Diagrama de clases: `../docs/04_Diagrama_UML_Clases.png`.
Convención: identificadores en mayúscula = públicos (+); en minúscula = privados (−).
