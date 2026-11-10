"""Reglas de los textos de una sesión: notas y nombre.

Spec 006 · RF-006-21, RF-006-22, RF-006-23 · RN-006-14, RN-006-15.
"""

import pytest

from reglas.errores import ErrorDeValidacion
from reglas.textos import NOMBRE_SESION_LIBRE, nombre_de_sesion_libre, validar_nota

# --- Notas (RN-006-14): opcionales, hasta 280 caracteres --------------------


def test_nota_valida_se_acepta():
    assert validar_nota("dormí mal") == "dormí mal"


def test_nota_se_guarda_sin_espacios_sobrantes():
    assert validar_nota("  subir a 35  ") == "subir a 35"


@pytest.mark.parametrize("entrada", [None, "", "   "])
def test_nota_es_opcional(entrada):
    assert validar_nota(entrada) == ""


def test_nota_de_280_caracteres_se_acepta():
    nota = "a" * 280

    assert validar_nota(nota) == nota


def test_nota_de_281_caracteres_se_rechaza_indicando_el_maximo():
    # CA-006-24b
    with pytest.raises(ErrorDeValidacion) as error:
        validar_nota("a" * 281)

    assert error.value.campo == "nota"
    assert error.value.mensaje == "La nota admite máximo 280 caracteres."


def test_el_limite_de_la_nota_se_mide_despues_de_quitar_espacios_sobrantes():
    assert validar_nota(" " + "a" * 280 + " ") == "a" * 280


@pytest.mark.parametrize("entrada", [123, ["x"], {"a": 1}, True])
def test_una_nota_que_no_es_texto_se_rechaza_en_lugar_de_romper(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_nota(entrada)

    assert error.value.campo == "nota"
    assert error.value.mensaje == "Escribe un texto válido."


@pytest.mark.parametrize("entrada", [123, ["x"], True])
def test_un_nombre_que_no_es_texto_se_rechaza_en_lugar_de_romper(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        nombre_de_sesion_libre(entrada)

    assert error.value.campo == "nombre"


# --- Nombre de una sesión libre (RF-006-21, RN-006-15) ----------------------


def test_sesion_libre_conserva_el_nombre_que_escribe_el_usuario():
    # CA-006-21a
    assert nombre_de_sesion_libre("Hotel Bogotá") == "Hotel Bogotá"


@pytest.mark.parametrize("entrada", [None, "", "   "])
def test_sesion_libre_sin_nombre_se_llama_sesion_libre(entrada):
    # CA-006-20a
    assert nombre_de_sesion_libre(entrada) == NOMBRE_SESION_LIBRE == "Sesión libre"


def test_nombre_de_50_caracteres_se_acepta():
    nombre = "n" * 50

    assert nombre_de_sesion_libre(nombre) == nombre


def test_nombre_de_51_caracteres_se_rechaza_indicando_el_maximo():
    with pytest.raises(ErrorDeValidacion) as error:
        nombre_de_sesion_libre("n" * 51)

    assert error.value.campo == "nombre"
    assert error.value.mensaje == "El nombre admite máximo 50 caracteres."
