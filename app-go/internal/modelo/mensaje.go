package modelo

import (
	"errors"
	"strings"
	"time"
	"unicode/utf8"
)

// MaxLongitudMensaje es el máximo de caracteres permitido en un mensaje.
const MaxLongitudMensaje = 1000

// Mensaje es un mensaje de texto enviado por un usuario autenticado.
type Mensaje struct {
	id             string
	remitenteID    string
	destinatarioID string
	contenido      string
	enviadoEn      time.Time
}

// NuevoMensaje construye un Mensaje y valida su contenido.
func NuevoMensaje(id, remitenteID, destinatarioID, contenido string, enviadoEn time.Time) (*Mensaje, error) {
	m := &Mensaje{id: id, remitenteID: remitenteID, destinatarioID: destinatarioID,
		contenido: contenido, enviadoEn: enviadoEn}
	if err := m.Validar(); err != nil {
		return nil, err
	}
	return m, nil
}

func (m *Mensaje) Contenido() string   { return m.contenido }
func (m *Mensaje) RemitenteID() string { return m.remitenteID }

// Validar comprueba las reglas de entrada del mensaje.
func (m *Mensaje) Validar() error {
	if m.remitenteID == "" {
		return errors.New("mensaje: remitente obligatorio")
	}
	if strings.TrimSpace(m.contenido) == "" {
		return errors.New("mensaje: el contenido no puede estar vacío")
	}
	if utf8.RuneCountInString(m.contenido) > MaxLongitudMensaje {
		return errors.New("mensaje: el contenido excede la longitud máxima")
	}
	return nil
}
