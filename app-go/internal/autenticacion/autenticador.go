// Package autenticacion define el contrato con el servicio de autenticación.
package autenticacion

import "github.com/Snto666/proyecto-integrador/app-go/internal/modelo"

// Autenticador abstrae al servicio de autenticación. La implementación real
// (AutenticadorFastAPI) se desarrolla en la Fase 4; en pruebas se puede usar
// una implementación simulada gracias al polimorfismo por interfaces.
type Autenticador interface {
	IniciarSesion(usuario, clave string) (*modelo.Sesion, error)
	ValidarToken(token string) (*modelo.Sesion, error)
}
