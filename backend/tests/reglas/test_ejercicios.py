"""Reglas de un ejercicio dentro de una sesión.

Spec 006 · RF-006-12, RF-006-13 · RN-006-05, RN-006-08.
Spec 002 · RN-002-07, RN-002-08 (nombre y grupo muscular).
"""

import pytest

from reglas.ejercicios import (
    clave_de_ejercicio,
    validar_grupo_muscular,
    validar_nombre_de_ejercicio,
    validar_numero_de_serie,
)
from reglas.errores import ErrorDeValidacion

# --- Nombre (RN-002-07): de 1 a 50 caracteres -------------------------------


def test_nombre_valido_se_guarda_sin_espacios_sobrantes():
    assert validar_nombre_de_ejercicio("  Press inclinado ") == "Press inclinado"


def test_nombre_de_50_caracteres_se_acepta():
    assert validar_nombre_de_ejercicio("e" * 50) == "e" * 50


@pytest.mark.parametrize("entrada", [None, "", "   "])
def test_nombre_vacio_se_rechaza(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_nombre_de_ejercicio(entrada)

    assert error.value.campo == "nombre"
    assert error.value.mensaje == "Escribe el nombre del ejercicio."


def test_nombre_de_51_caracteres_se_rechaza():
    with pytest.raises(ErrorDeValidacion) as error:
        validar_nombre_de_ejercicio("e" * 51)

    assert error.value.mensaje == "El nombre del ejercicio admite máximo 50 caracteres."


# --- Grupo muscular (RN-002-08): obligatorio, hasta 30 caracteres -----------


def test_grupo_valido_se_guarda_sin_espacios_sobrantes():
    assert validar_grupo_muscular(" Pecho ") == "Pecho"


@pytest.mark.parametrize("entrada", [None, "", "  "])
def test_grupo_vacio_se_rechaza(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_grupo_muscular(entrada)

    assert error.value.campo == "grupo"
    assert error.value.mensaje == "Elige el grupo muscular."


def test_grupo_de_31_caracteres_se_rechaza():
    with pytest.raises(ErrorDeValidacion) as error:
        validar_grupo_muscular("g" * 31)

    assert error.value.mensaje == "El grupo muscular admite máximo 30 caracteres."


# --- Número de serie (RN-006-05): de 1 a 10 por ejercicio -------------------


@pytest.mark.parametrize("numero", [1, 3, 10])
def test_numero_de_serie_valido(numero):
    assert validar_numero_de_serie(numero) == numero


@pytest.mark.parametrize("numero", [0, 11, -1, 2.5, "3", None, True])
def test_numero_de_serie_invalido(numero):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_numero_de_serie(numero)

    assert error.value.campo == "numero"
    assert error.value.mensaje == "Un ejercicio admite entre 1 y 10 series."


# --- Clave para reconocer el mismo ejercicio (RN-002-07, RN-006-08) ---------


@pytest.mark.parametrize(
    "variante",
    ["Press inclinado", "press inclinado", "  PRESS   INCLINADO ", "Préss Inclinádo"],
)
def test_el_mismo_ejercicio_se_reconoce_sin_importar_mayusculas_tildes_ni_espacios(variante):
    assert clave_de_ejercicio(variante) == "press inclinado"


def test_ejercicios_distintos_tienen_claves_distintas():
    assert clave_de_ejercicio("Press inclinado") != clave_de_ejercicio("Press declinado")


def test_la_enie_no_se_confunde_con_la_ene():
    # "Peña" y "Pena" son palabras distintas en español.
    assert clave_de_ejercicio("Peña") != clave_de_ejercicio("Pena")
