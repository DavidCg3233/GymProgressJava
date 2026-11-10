"""Reglas del ciclo de vida de una sesión de entrenamiento.

Spec 006 · RF-006-08, RF-006-19 · RN-006-06, RN-006-09, RN-006-12.
"""

from datetime import datetime, timedelta, timezone

import pytest

from reglas.sesiones import (
    DURACION_MAXIMA,
    debe_cerrarse,
    debe_descartarse,
    hora_de_cierre_automatico,
)

BOGOTA = timezone(timedelta(hours=-5))
INICIO = datetime(2026, 11, 9, 18, 0, tzinfo=BOGOTA)  # 6:00 p. m., como en CA-006-08a


def test_la_duracion_maxima_de_una_sesion_es_de_dos_horas():
    assert DURACION_MAXIMA == timedelta(hours=2)


def test_la_hora_de_cierre_automatico_es_el_inicio_mas_dos_horas():
    # RN-006-12
    assert hora_de_cierre_automatico(INICIO) == datetime(2026, 11, 9, 20, 0, tzinfo=BOGOTA)


@pytest.mark.parametrize(
    ("ahora", "esperado"),
    [
        pytest.param(INICIO, False, id="recien empezada"),
        pytest.param(INICIO + timedelta(hours=1, minutes=59, seconds=59), False, id="un segundo antes de las 2 horas"),
        pytest.param(INICIO + timedelta(hours=2), True, id="justo a las 2 horas"),
        pytest.param(INICIO + timedelta(hours=2, minutes=1), True, id="CA-006-08a: 8:01 p. m."),
        pytest.param(INICIO + timedelta(days=3), True, id="dias despues"),
    ],
)
def test_una_sesion_en_curso_se_cierra_al_cumplir_dos_horas(ahora, esperado):
    assert debe_cerrarse(INICIO, ahora) is esperado


def test_el_cierre_no_depende_de_la_zona_horaria_en_que_se_exprese_la_hora():
    ocho_y_uno_en_utc = datetime(2026, 11, 10, 1, 1, tzinfo=timezone.utc)  # 8:01 p. m. en Bogotá

    assert debe_cerrarse(INICIO, ocho_y_uno_en_utc) is True


def test_no_se_aceptan_horas_sin_zona_horaria():
    # Una hora sin zona es ambigua: compararla daría un cierre equivocado.
    sin_zona = datetime(2026, 11, 9, 20, 1)

    with pytest.raises(ValueError, match="zona horaria"):
        debe_cerrarse(INICIO, sin_zona)


@pytest.mark.parametrize(
    ("series_confirmadas", "esperado"),
    [
        pytest.param(0, True, id="CA-006-19a: sin series confirmadas"),
        pytest.param(1, False, id="con una serie confirmada"),
        pytest.param(5, False, id="CA-006-08a: con cinco series"),
    ],
)
def test_una_sesion_terminada_sin_series_confirmadas_se_descarta(series_confirmadas, esperado):
    assert debe_descartarse(series_confirmadas) is esperado


def test_la_cantidad_de_series_confirmadas_no_puede_ser_negativa():
    with pytest.raises(ValueError):
        debe_descartarse(-1)
