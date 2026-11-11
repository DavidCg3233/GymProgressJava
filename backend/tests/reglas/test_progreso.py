"""Reglas de progreso (T-004-01).

Spec 004 · RN-004-02 a 09 · plan 004, secciones 5 y 6.
Los números son los de los criterios CA-004-04a, 04b y 09a.
"""

from datetime import date
from decimal import Decimal

import pytest

from reglas.errores import ErrorDeValidacion
from reglas.progreso import (
    SerieHecha,
    cumple,
    es_de_peso_corporal,
    inicio_de_semana,
    mejor_serie,
    ordenar_grupos,
    sesiones_por_semana,
    validar_meta,
    volumen,
)


def serie(peso: str, reps: int, cuando=0) -> SerieHecha:
    return SerieHecha(peso=Decimal(peso), reps=reps, cuando=cuando)


# --- Récord y serie más pesada (RN-004-03, 04, 05) ---------------------------


def test_ca_004_04a_record_mayor_peso_luego_mas_reps_luego_el_mas_antiguo():
    series = [
        serie("32.5", 8, date(2026, 11, 2)),
        serie("35", 5, date(2026, 11, 9)),
        serie("35", 6, date(2026, 11, 16)),
        serie("35", 6, date(2026, 11, 23)),
        serie("30", 15, date(2026, 11, 23)),
    ]

    assert mejor_serie(series) == serie("35", 6, date(2026, 11, 16))


def test_el_orden_en_que_llegan_las_series_no_cambia_el_record():
    antigua = serie("35", 6, date(2026, 11, 16))
    nueva = serie("35", 6, date(2026, 11, 23))

    assert mejor_serie([nueva, antigua]) == antigua


def test_ca_004_04b_peso_corporal_gana_la_de_mas_reps():
    series = [serie("0", 8), serie("0", 10)]

    assert es_de_peso_corporal(series) is True
    assert mejor_serie(series) == serie("0", 10)


def test_un_ejercicio_con_alguna_serie_con_peso_no_es_de_peso_corporal():
    assert es_de_peso_corporal([serie("0", 12), serie("5", 8)]) is False


def test_sin_series_no_hay_record():
    assert mejor_serie([]) is None
    assert es_de_peso_corporal([]) is False


def test_ca_004_09a_serie_mas_pesada_de_una_sesion():
    sesion = [serie("30", 10), serie("32.5", 8), serie("32.5", 6)]

    assert mejor_serie(sesion).peso == Decimal("32.5")
    assert mejor_serie(sesion).reps == 8


# --- Volumen (RN-004-06) ----------------------------------------------------


def test_ca_004_09a_volumen_es_la_suma_de_peso_por_reps_exacta():
    sesion = [serie("30", 10), serie("32.5", 8), serie("32.5", 6)]

    assert volumen(sesion, peso_corporal=False) == Decimal("755")


def test_volumen_de_peso_corporal_es_la_suma_de_reps():
    assert volumen([serie("0", 8), serie("0", 10)], peso_corporal=True) == 18


def test_volumen_sin_series_es_cero():
    assert volumen([], peso_corporal=False) == 0


# --- Semana (RN-004-02) -----------------------------------------------------


@pytest.mark.parametrize(
    ("dia", "lunes"),
    [
        pytest.param(date(2026, 11, 9), date(2026, 11, 9), id="un lunes es su propio inicio"),
        pytest.param(date(2026, 11, 12), date(2026, 11, 9), id="jueves"),
        pytest.param(date(2026, 11, 15), date(2026, 11, 9), id="CA-004-05b: el domingo es de la semana que termina"),
        pytest.param(date(2026, 11, 16), date(2026, 11, 16), id="el lunes siguiente empieza otra"),
        pytest.param(date(2027, 1, 1), date(2026, 12, 28), id="cruza el cambio de año"),
    ],
)
def test_la_semana_empieza_el_lunes(dia, lunes):
    assert inicio_de_semana(dia) == lunes


def test_doce_semanas_de_la_mas_antigua_a_la_actual_con_ceros():
    hoy = date(2026, 11, 12)  # jueves
    fechas = [date(2026, 11, 9), date(2026, 11, 11), date(2026, 11, 3), date(2026, 8, 20)]

    semanas = sesiones_por_semana(fechas, hoy)

    assert len(semanas) == 12
    assert semanas[-1] == (date(2026, 11, 9), 2)
    assert semanas[-2] == (date(2026, 11, 2), 1)
    assert semanas[0] == (date(2026, 8, 24), 0)
    assert sum(cantidad for _, cantidad in semanas) == 3  # la de agosto 20 queda fuera


def test_una_sesion_futura_no_cuenta():
    assert sesiones_por_semana([date(2026, 11, 20)], date(2026, 11, 12))[-1] == (date(2026, 11, 9), 0)


# --- Meta (RN-004-08) -------------------------------------------------------


@pytest.mark.parametrize(
    ("sesiones", "meta", "esperado"),
    [
        pytest.param(3, 4, False, id="CA-004-05a: 3 de 4 no cumple"),
        pytest.param(4, 4, True, id="igual a la meta cumple"),
        pytest.param(5, 4, True, id="mas que la meta cumple"),
        pytest.param(9, None, None, id="sin meta no se juzga"),
    ],
)
def test_cumple(sesiones, meta, esperado):
    assert cumple(sesiones, meta) is esperado


@pytest.mark.parametrize("valor", [1, 4, 14, None])
def test_meta_valida(valor):
    assert validar_meta(valor) == valor


@pytest.mark.parametrize("valor", [0, 15, -1, 2.5, "4", "", True])
def test_meta_invalida(valor):
    with pytest.raises(ErrorDeValidacion) as error:
        validar_meta(valor)

    assert (error.value.campo, error.value.mensaje) == ("meta", "La meta va de 1 a 14 sesiones por semana.")


# --- Grupos (RN-004-09 y regla nueva 1) -------------------------------------


def test_ca_004_06a_grupos_de_mayor_a_menor_con_ceros():
    assert ordenar_grupos({"Pierna": 0, "Bíceps": 4, "Pecho": 9}) == [("Pecho", 9), ("Bíceps", 4), ("Pierna", 0)]


def test_empates_por_nombre_sin_mayusculas_ni_tildes():
    assert ordenar_grupos({"pierna": 3, "Abdomen": 3, "Bíceps": 3}) == [("Abdomen", 3), ("Bíceps", 3), ("pierna", 3)]
