package modelo

import (
	"errors"
	"time"
)

// Sesion es la sesión emitida por el servicio de autenticación.
type Sesion struct {
	token     string
	usuarioID string
	expiraEn  time.Time
}

// NuevaSesion construye una Sesion a partir de la respuesta de FastAPI.
func NuevaSesion(token, usuarioID string, expiraEn time.Time) (*Sesion, error) {
	if token == "" || usuarioID == "" {
		return nil, errors.New("sesion: token y usuario son obligatorios")
	}
	return &Sesion{token: token, usuarioID: usuarioID, expiraEn: expiraEn}, nil
}

func (s *Sesion) Token() string     { return s.token }
func (s *Sesion) UsuarioID() string { return s.usuarioID }

// EsValida indica si la sesión aún no ha expirado.
func (s *Sesion) EsValida() bool { return time.Now().Before(s.expiraEn) }
