"""Errores que producen las reglas de negocio."""


class ErrorDeValidacion(Exception):
    """Un dato del usuario no cumple una regla.

    `campo` dice cuál dato falló y `mensaje` es el texto que ve el usuario:
    en español, sin términos técnicos y con el rango permitido cuando aplica
    (RF-006-24, RNF-USA-02).
    """

    def __init__(self, campo: str, mensaje: str) -> None:
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje
