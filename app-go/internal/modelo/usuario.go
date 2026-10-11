// Package modelo contiene las entidades del dominio del chat.
package modelo

import "errors"

// Usuario representa a un empleado autenticado por el servicio FastAPI.
// El servidor Go no registra usuarios ni guarda contraseñas.
type Usuario struct {
	id            string
	nombreUsuario string
	rol           string
}

// NuevoUsuario valida los datos y construye un Usuario.
func NuevoUsuario(id, nombreUsuario, rol string) (*Usuario, error) {
	if id == "" || nombreUsuario == "" {
		return nil, errors.New("usuario: id y nombre de usuario son obligatorios")
	}
	if rol != "empleado" && rol != "admin" {
		return nil, errors.New("usuario: rol inválido")
	}
	return &Usuario{id: id, nombreUsuario: nombreUsuario, rol: rol}, nil
}

func (u *Usuario) ID() string            { return u.id }
func (u *Usuario) NombreUsuario() string { return u.nombreUsuario }
func (u *Usuario) Rol() string           { return u.rol }
func (u *Usuario) EsAdmin() bool         { return u.rol == "admin" }
