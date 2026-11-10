"""Reglas de los textos de una sesión: notas y nombre (spec 006)."""

from .errores import ErrorDeValidacion

# RN-006-14: notas de sesión y de ejercicio, opcionales.
LARGO_MAXIMO_NOTA = 280

# RN-006-15 y RF-006-21: nombre de una sesión libre.
LARGO_MAXIMO_NOMBRE = 50
NOMBRE_SESION_LIBRE = "Sesión libre"


def validar_nota(valor: str | None) -> str:
    """Devuelve la nota sin espacios sobrantes. Vacía es válida: la nota es opcional."""
    nota = _limpiar(valor, "nota")
    if len(nota) > LARGO_MAXIMO_NOTA:
        raise ErrorDeValidacion("nota", f"La nota admite máximo {LARGO_MAXIMO_NOTA} caracteres.")
    return nota


def nombre_de_sesion_libre(valor: str | None) -> str:
    """Devuelve el nombre que escribió el usuario, o el nombre por defecto si lo dejó vacío."""
    nombre = _limpiar(valor, "nombre")
    if len(nombre) > LARGO_MAXIMO_NOMBRE:
        raise ErrorDeValidacion("nombre", f"El nombre admite máximo {LARGO_MAXIMO_NOMBRE} caracteres.")
    return nombre or NOMBRE_SESION_LIBRE


def _limpiar(valor: str | None, campo: str) -> str:
    return exigir_texto(valor, campo).strip()


def exigir_texto(valor: object, campo: str) -> str:
    """Acepta un texto o nada. Cualquier otro tipo es un dato mal formado, no un error nuestro."""
    if valor is None:
        return ""
    if not isinstance(valor, str):
        raise ErrorDeValidacion(campo, "Escribe un texto válido.")
    return valor
