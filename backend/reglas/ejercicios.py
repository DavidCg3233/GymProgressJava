"""Reglas de un ejercicio dentro de una sesión (specs 006 y 002)."""

import unicodedata

from .errores import ErrorDeValidacion
from .textos import exigir_texto

# RN-002-07 y RN-002-08.
LARGO_MAXIMO_NOMBRE_DE_EJERCICIO = 50
LARGO_MAXIMO_GRUPO = 30

# RN-006-05.
SERIES_MINIMAS = 1
SERIES_MAXIMAS = 10

_TILDE_DE_LA_ENIE = "̃"


def validar_nombre_de_ejercicio(valor: str | None) -> str:
    nombre = exigir_texto(valor, "nombre").strip()
    if not nombre:
        raise ErrorDeValidacion("nombre", "Escribe el nombre del ejercicio.")
    if len(nombre) > LARGO_MAXIMO_NOMBRE_DE_EJERCICIO:
        raise ErrorDeValidacion(
            "nombre", f"El nombre del ejercicio admite máximo {LARGO_MAXIMO_NOMBRE_DE_EJERCICIO} caracteres."
        )
    return nombre


def validar_grupo_muscular(valor: str | None) -> str:
    grupo = exigir_texto(valor, "grupo").strip()
    if not grupo:
        raise ErrorDeValidacion("grupo", "Elige el grupo muscular.")
    if len(grupo) > LARGO_MAXIMO_GRUPO:
        raise ErrorDeValidacion("grupo", f"El grupo muscular admite máximo {LARGO_MAXIMO_GRUPO} caracteres.")
    return grupo


def validar_numero_de_serie(valor: object) -> int:
    es_entero = isinstance(valor, int) and not isinstance(valor, bool)
    if not es_entero or not SERIES_MINIMAS <= valor <= SERIES_MAXIMAS:
        raise ErrorDeValidacion("numero", f"Un ejercicio admite entre {SERIES_MINIMAS} y {SERIES_MAXIMAS} series.")
    return valor


def clave_de_ejercicio(nombre: str) -> str:
    """Forma canónica del nombre, para reconocer el mismo ejercicio escrito de otra manera.

    Ignora mayúsculas, tildes y espacios repetidos (RN-002-07), pero conserva
    la ñ: en español es otra letra, no una n con adorno.
    """
    descompuesto = unicodedata.normalize("NFD", nombre.casefold())
    sin_tildes = "".join(
        caracter
        for caracter in descompuesto
        if not unicodedata.combining(caracter) or caracter == _TILDE_DE_LA_ENIE
    )
    return " ".join(unicodedata.normalize("NFC", sin_tildes).split())
