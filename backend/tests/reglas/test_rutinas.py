"""Reglas de una rutina (T-002-01).

Spec 002 · RF-002-03, 04, 21 · RN-002-01 a 04 · plan 002, sección 6.
La tabla de bordes es la de CA-002-RN. Su espejo en JavaScript es
frontend/src/reglas/rutinas.test.js y debe coincidir caso por caso.
"""

import pytest

from reglas.errores import ErrorDeValidacion
from reglas.rutinas import (
    MAXIMO_DE_EJERCICIOS,
    bits_a_dias,
    dias_a_bits,
    nombre_de_copia,
    tiene_dia,
    validar_dias,
    validar_ejercicios_de_rutina,
    validar_nombre_de_rutina,
    validar_series_previstas,
)


def falla(accion, *argumentos) -> ErrorDeValidacion:
    with pytest.raises(ErrorDeValidacion) as error:
        accion(*argumentos)
    return error.value


# --- Nombre (RN-002-01) -----------------------------------------------------


def test_nombre_valido_sin_espacios_sobrantes():
    assert validar_nombre_de_rutina("  Pecho ") == "Pecho"


def test_ca_002_rn_nombre_de_50_caracteres_se_acepta():
    assert validar_nombre_de_rutina("r" * 50) == "r" * 50


def test_ca_002_rn_nombre_de_51_caracteres_se_rechaza():
    error = falla(validar_nombre_de_rutina, "r" * 51)

    assert (error.campo, error.mensaje) == ("nombre", "El nombre de la rutina admite máximo 50 caracteres.")


@pytest.mark.parametrize("valor", [None, "", "   "])
def test_ca_002_03a_sin_nombre_se_rechaza(valor):
    error = falla(validar_nombre_de_rutina, valor)

    assert (error.campo, error.mensaje) == ("nombre", "Escribe el nombre de la rutina.")


def test_un_nombre_que_no_es_texto_se_rechaza():
    assert falla(validar_nombre_de_rutina, 5).campo == "nombre"


# --- Días (RN-002-02) -------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        pytest.param([], [], id="ningun dia"),
        pytest.param([1], [1], id="solo lunes"),
        pytest.param([4, 1], [1, 4], id="lunes y jueves, en orden"),
        pytest.param([1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7], id="toda la semana"),
    ],
)
def test_dias_validos(entrada, esperado):
    assert validar_dias(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param([0], id="cero"),
        pytest.param([8], id="ocho"),
        pytest.param([1, 1], id="repetido"),
        pytest.param(["lunes"], id="texto"),
        pytest.param([True], id="booleano"),
        pytest.param(None, id="vacio"),
        pytest.param("1,4", id="texto en vez de lista"),
    ],
)
def test_dias_invalidos_se_rechazan(entrada):
    error = falla(validar_dias, entrada)

    assert (error.campo, error.mensaje) == ("dias", "Los días van de lunes (1) a domingo (7), sin repetir.")


@pytest.mark.parametrize(
    ("dias", "bits"),
    [([], 0), ([1], 1), ([7], 64), ([1, 4], 9), ([1, 2, 3, 4, 5, 6, 7], 127)],
)
def test_los_dias_se_guardan_como_bits_y_vuelven_igual(dias, bits):
    assert dias_a_bits(dias) == bits
    assert bits_a_dias(bits) == dias


def test_tiene_dia_dice_si_la_rutina_toca_ese_dia():
    lunes_y_jueves = dias_a_bits([1, 4])

    assert [tiene_dia(lunes_y_jueves, dia) for dia in range(1, 8)] == [True, False, False, True, False, False, False]


# --- Ejercicios de la rutina (RN-002-03) ------------------------------------


def test_ca_002_rn_veinte_ejercicios_se_aceptan():
    validar_ejercicios_de_rutina([f"ejercicio {n}" for n in range(20)])


def test_ca_002_rn_veintiun_ejercicios_se_rechazan():
    error = falla(validar_ejercicios_de_rutina, [f"ejercicio {n}" for n in range(21)])

    assert (error.campo, error.mensaje) == ("ejercicios", "Una rutina admite máximo 20 ejercicios.")
    assert MAXIMO_DE_EJERCICIOS == 20


def test_ca_002_03a_sin_ejercicios_se_rechaza():
    error = falla(validar_ejercicios_de_rutina, [])

    assert (error.campo, error.mensaje) == ("ejercicios", "Agrega al menos un ejercicio.")


def test_ca_002_rn_el_mismo_ejercicio_dos_veces_se_rechaza():
    error = falla(validar_ejercicios_de_rutina, ["press inclinado", "fondos", "press inclinado"])

    assert (error.campo, error.mensaje) == ("ejercicios", "Un ejercicio aparece una sola vez por rutina.")


# --- Series previstas (RN-002-04) -------------------------------------------


@pytest.mark.parametrize("valor", [1, 3, 10])
def test_ca_002_rn_series_validas(valor):
    assert validar_series_previstas(valor) == valor


@pytest.mark.parametrize("valor", [0, 11, 2.5, "3", None, True])
def test_ca_002_rn_series_invalidas(valor):
    error = falla(validar_series_previstas, valor)

    assert (error.campo, error.mensaje) == ("series", "Las series previstas van de 1 a 10.")


# --- Nombre de una copia (RF-002-21, plan 002 sección 6) --------------------


def test_ca_002_21a_la_primera_copia_se_llama_copia():
    assert nombre_de_copia("Pecho", existentes=["Pecho"]) == "Pecho (copia)"


def test_la_segunda_copia_se_numera_para_no_repetir_nombre():
    assert nombre_de_copia("Pecho", existentes=["Pecho", "Pecho (copia)"]) == "Pecho (copia 2)"


def test_la_numeracion_sigue_hasta_encontrar_uno_libre():
    existentes = ["Pecho", "Pecho (copia)", "Pecho (copia 2)", "pecho (COPIA 3)"]

    assert nombre_de_copia("Pecho", existentes=existentes) == "Pecho (copia 4)"


def test_la_copia_nunca_pasa_de_50_caracteres():
    original = "r" * 50

    copia = nombre_de_copia(original, existentes=[original])

    assert len(copia) == 50
    assert copia.endswith(" (copia)")
