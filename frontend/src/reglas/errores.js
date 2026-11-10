// Errores que producen las reglas de negocio.

/**
 * Un dato del usuario no cumple una regla.
 *
 * `campo` dice cuál dato falló y `mensaje` es el texto que ve el usuario:
 * en español, sin términos técnicos y con el rango permitido cuando aplica
 * (RF-006-24, RNF-USA-02).
 */
export class ErrorDeValidacion extends Error {
  constructor(campo, mensaje) {
    super(mensaje)
    this.name = 'ErrorDeValidacion'
    this.campo = campo
    this.mensaje = mensaje
  }
}
