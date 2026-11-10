"""Reglas de una serie: peso y repeticiones.

Spec 006 · RF-006-24 · RN-006-02, RN-006-03, RN-006-04.
Las tablas son las del criterio de aceptación CA-006-24a.
"""

from decimal import Decimal

import pytest

from reglas.errores import ErrorDeValidacion
from reglas.series import validar_peso, validar_repeticiones

# --- Peso (RN-006-02): de 0 a 500 kg, en múltiplos de 0,5 -------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        pytest.param("0", Decimal("0"), id="CA-006-24a: 0 es peso corporal"),
        pytest.param("0.5", Decimal("0.5"), id="el paso minimo"),
        pytest.param("32.5", Decimal("32.5"), id="un valor intermedio"),
        pytest.param("500", Decimal("500"), id="CA-006-24a: 500 es el maximo"),
        pytest.param(30, Decimal("30"), id="acepta enteros"),
        pytest.param(Decimal("32.5"), Decimal("32.5"), id="acepta decimales exactos"),
        pytest.param(32.5, Decimal("32.5"), id="acepta numeros de coma flotante"),
        pytest.param("32,5", Decimal("32.5"), id="acepta coma decimal, como se escribe en Colombia"),
    ],
)
def test_peso_valido_se_acepta_y_se_devuelve_como_decimal(entrada, esperado):
    assert validar_peso(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param("-0.5", id="CA-006-24a: -0,5 esta bajo el minimo"),
        pytest.param("500.5", id="CA-006-24a: 500,5 supera el maximo"),
        pytest.param("1000", id="muy por encima del maximo"),
    ],
)
def test_peso_fuera_de_rango_se_rechaza_indicando_el_rango(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_peso(entrada)

    assert error.value.campo == "peso"
    assert error.value.mensaje == "El peso debe estar entre 0 y 500 kg."


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param("30.3", id="CA-006-24a: 30,3 no es multiplo de 0,5"),
        pytest.param("0.25", id="la mitad del paso"),
        pytest.param(30.3, id="coma flotante que no cae en el paso"),
    ],
)
def test_peso_que_no_es_multiplo_del_paso_se_rechaza(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_peso(entrada)

    assert error.value.campo == "peso"
    assert error.value.mensaje == "El peso va de a 0,5 kg."


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param(None, id="CA-006-24a: vacio"),
        pytest.param("", id="texto vacio"),
        pytest.param("   ", id="solo espacios"),
    ],
)
def test_peso_vacio_se_rechaza_pidiendo_el_dato(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_peso(entrada)

    assert error.value.campo == "peso"
    assert error.value.mensaje == "Escribe el peso."


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param("treinta", id="texto"),
        pytest.param("NaN", id="no es un numero"),
        pytest.param("Infinity", id="infinito"),
        pytest.param(True, id="un booleano no es un peso"),
    ],
)
def test_peso_que_no_es_un_numero_se_rechaza(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_peso(entrada)

    assert error.value.campo == "peso"
    assert error.value.mensaje == "El peso debe ser un número."


# --- Repeticiones (RN-006-04): entero de 1 a 100 ----------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        pytest.param(1, 1, id="CA-006-24a: 1 es el minimo"),
        pytest.param(8, 8, id="un valor intermedio"),
        pytest.param(100, 100, id="CA-006-24a: 100 es el maximo"),
        pytest.param("10", 10, id="acepta texto con un entero"),
        pytest.param(Decimal("8"), 8, id="acepta un decimal sin parte fraccionaria"),
    ],
)
def test_repeticiones_validas_se_aceptan_y_se_devuelven_como_entero(entrada, esperado):
    resultado = validar_repeticiones(entrada)

    assert resultado == esperado
    assert type(resultado) is int


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param(0, id="CA-006-24a: 0 esta bajo el minimo"),
        pytest.param(101, id="CA-006-24a: 101 supera el maximo"),
        pytest.param(-3, id="negativo"),
    ],
)
def test_repeticiones_fuera_de_rango_se_rechazan_indicando_el_rango(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_repeticiones(entrada)

    assert error.value.campo == "reps"
    assert error.value.mensaje == "Las repeticiones deben estar entre 1 y 100."


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param(8.5, id="CA-006-24a: 8,5 no es entero"),
        pytest.param("8.5", id="texto con decimales"),
        pytest.param("ocho", id="texto"),
        pytest.param(True, id="un booleano no es una cantidad"),
    ],
)
def test_repeticiones_que_no_son_un_entero_se_rechazan(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_repeticiones(entrada)

    assert error.value.campo == "reps"
    assert error.value.mensaje == "Las repeticiones deben ser un número entero."


@pytest.mark.parametrize("entrada", [None, "", "  "])
def test_repeticiones_vacias_se_rechazan_pidiendo_el_dato(entrada):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_repeticiones(entrada)

    assert error.value.campo == "reps"
    assert error.value.mensaje == "Escribe las repeticiones."
