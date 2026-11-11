"""Reglas del cuerpo: peso, estatura, fecha, IMC y objetivo (T-003-01).

Spec 003 · RN-003-01 a 05, 08 · plan 003, secciones 5 y 6.
Las tablas son las de CA-003-05b y CA-003-13a.
"""

from datetime import date
from decimal import Decimal

import pytest

from reglas.cuerpo import (
    categoria_de_imc,
    cambio,
    hacia_el_objetivo,
    imc,
    imc_para_mostrar,
    validar_estatura,
    validar_fecha_de_peso,
    validar_peso_corporal,
)
from reglas.errores import ErrorDeValidacion

HOY = date(2026, 11, 11)
D = Decimal


def falla(accion):
    with pytest.raises(ErrorDeValidacion) as error:
        accion()
    return error.value.campo, error.value.mensaje


# --- Peso (RN-003-03) -------------------------------------------------------


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        pytest.param("20.0", D("20.0"), id="CA-003-13a: 20,0 se acepta"),
        pytest.param("300.0", D("300.0"), id="CA-003-13a: 300,0 se acepta"),
        pytest.param("79,5", D("79.5"), id="con coma decimal"),
        pytest.param(79, D("79"), id="entero"),
        pytest.param(78.5, D("78.5"), id="numero con decimales"),
    ],
)
def test_peso_valido(valor, esperado):
    assert validar_peso_corporal(valor) == esperado


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param("19.9", id="CA-003-13a: 19,9 se rechaza"),
        pytest.param("300.1", id="CA-003-13a: 300,1 se rechaza"),
        pytest.param("79.55", id="mas de un decimal"),
        pytest.param("abc", id="no es numero"),
        pytest.param(True, id="booleano"),
        pytest.param("NaN", id="no es un numero finito"),
    ],
)
def test_peso_invalido(valor):
    assert falla(lambda: validar_peso_corporal(valor)) == ("peso", "El peso va de 20 a 300 kg, con un decimal.")


@pytest.mark.parametrize("valor", [None, "", "  "])
def test_peso_vacio(valor):
    assert falla(lambda: validar_peso_corporal(valor)) == ("peso", "Escribe tu peso.")


# --- Estatura (RN-003-04) ---------------------------------------------------


@pytest.mark.parametrize("valor", [100, 175, 250])
def test_estatura_valida(valor):
    assert validar_estatura(valor) == valor


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(99, id="CA-003-13a: 99 se rechaza"),
        pytest.param(251, id="CA-003-13a: 251 se rechaza"),
        pytest.param(1.75, id="CA-003-13a: 1,75 va en centimetros"),
        pytest.param(175.5, id="con decimales"),
        pytest.param("175", id="texto"),
        pytest.param(True, id="booleano"),
        pytest.param(None, id="vacia"),
    ],
)
def test_estatura_invalida(valor):
    assert falla(lambda: validar_estatura(valor)) == ("estatura", "La estatura va en centímetros, de 100 a 250.")


# --- Fecha (RN-003-05) ------------------------------------------------------


@pytest.mark.parametrize("valor", [HOY, "2026-11-11", "2020-02-29"])
def test_fecha_valida(valor):
    assert validar_fecha_de_peso(valor, HOY) == (valor if isinstance(valor, date) else date.fromisoformat(valor))


def test_ca_003_13a_manana_se_rechaza():
    assert falla(lambda: validar_fecha_de_peso("2026-11-12", HOY)) == ("fecha", "La fecha no puede ser futura.")


@pytest.mark.parametrize("valor", [None, "", "11/11/2026", "2026-02-30", 20261111])
def test_fecha_invalida(valor):
    assert falla(lambda: validar_fecha_de_peso(valor, HOY)) == ("fecha", "Escribe una fecha válida.")


# --- IMC (RN-003-01, 02) ----------------------------------------------------


def test_ca_003_01a_imc_de_79_kg_con_175_cm():
    exacto = imc(D("79.0"), 175)

    assert imc_para_mostrar(exacto) == D("25.8")
    assert categoria_de_imc(exacto) == "Sobrepeso"


@pytest.mark.parametrize(
    ("peso", "exacto", "mostrado", "categoria"),
    [
        ("73.9", "18.475", "18.5", "Bajo peso"),
        ("74.0", "18.5", "18.5", "Normal"),
        ("99.9", "24.975", "25.0", "Normal"),
        ("100.0", "25", "25.0", "Sobrepeso"),
        ("119.9", "29.975", "30.0", "Sobrepeso"),
        ("120.0", "30", "30.0", "Obesidad"),
    ],
    ids=lambda valor: str(valor),
)
def test_ca_003_05b_la_categoria_se_decide_sin_redondear(peso, exacto, mostrado, categoria):
    valor = imc(D(peso), 200)

    assert valor == D(exacto)
    assert imc_para_mostrar(valor) == D(mostrado)
    assert categoria_de_imc(valor) == categoria


def test_el_medio_decimal_sube():
    # Plan 003, regla nueva 2: 18,45 se muestra 18,5 (el redondeo bancario daría 18,4).
    assert imc_para_mostrar(D("18.45")) == D("18.5")


# --- Cambio (RF-003-04) -----------------------------------------------------


@pytest.mark.parametrize(
    ("anterior", "actual", "esperado"),
    [
        ("80.0", "79.0", (D("1.0"), "bajo")),
        ("79.0", "80.5", (D("1.5"), "subio")),
        ("79.0", "79.0", (D("0.0"), "igual")),
    ],
)
def test_cambio(anterior, actual, esperado):
    assert cambio(D(anterior), D(actual)) == esperado


# --- Objetivo (RN-003-08 y regla nueva 1) -----------------------------------


def test_ca_003_08a_faltan_4_por_bajar():
    assert hacia_el_objetivo(D("80.0"), D("79.0"), D("75")) == {"faltan": D("4.0"), "direccion": "bajar", "alcanzado": False}


def test_ca_003_09a_cruzar_el_objetivo_es_alcanzarlo():
    assert hacia_el_objetivo(D("80.0"), D("74.8"), D("75.0"))["alcanzado"] is True


@pytest.mark.parametrize(
    ("actual", "alcanzado"),
    [("75.0", True), ("75.1", False)],
)
def test_bajar_se_alcanza_al_llegar_o_pasar(actual, alcanzado):
    assert hacia_el_objetivo(D("80.0"), D(actual), D("75.0"))["alcanzado"] is alcanzado


def test_subir():
    resultado = hacia_el_objetivo(D("60.0"), D("62.0"), D("65.0"))

    assert resultado == {"faltan": D("3.0"), "direccion": "subir", "alcanzado": False}
    assert hacia_el_objetivo(D("60.0"), D("65.2"), D("65.0"))["alcanzado"] is True


def test_alcanzado_no_tiene_faltante():
    assert hacia_el_objetivo(D("80.0"), D("74.8"), D("75.0"))["faltan"] == D("0")


@pytest.mark.parametrize(
    ("actual", "esperado"),
    [
        ("70.0", {"faltan": D("0"), "direccion": "mantener", "alcanzado": True}),
        ("71.5", {"faltan": D("1.5"), "direccion": "bajar", "alcanzado": False}),
        ("69.0", {"faltan": D("1.0"), "direccion": "subir", "alcanzado": False}),
    ],
)
def test_objetivo_igual_al_primer_registro_es_mantener(actual, esperado):
    # Plan 003, regla nueva 1.
    assert hacia_el_objetivo(D("70.0"), D(actual), D("70.0")) == esperado
