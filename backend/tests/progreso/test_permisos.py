"""Progreso no mezcla cuentas ni se abre sin acceso (T-004-09).

RNF-ACC-06 · plan 004, sección 7.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

pytestmark = pytest.mark.django_db

HACE_UN_RATO = datetime(2026, 11, 9, 18, tzinfo=ZoneInfo("America/Bogota"))


def test_las_series_de_otra_cuenta_no_suman_en_nada(api, otra):
    otra.put("/api/progreso/meta/", meta=3)
    otra.sesion_terminada([(100, 5)], inicio=HACE_UN_RATO)

    assert api.get("/api/progreso/").json() == {"vacio": True, "meta": None, "semanas": [], "grupos": [], "records": []}
    assert api.get("/api/progreso/evolucion/?clave=press inclinado").status_code == 404


def test_cada_cuenta_ve_solo_su_record(api, otra):
    api.sesion_terminada([(30, 10)], inicio=HACE_UN_RATO)
    otra.sesion_terminada([(100, 5)], inicio=HACE_UN_RATO)

    mio = api.get("/api/progreso/").json()

    assert [(r["peso"], r["reps"]) for r in mio["records"]] == [(30.0, 10)]
    assert sum(semana["sesiones"] for semana in mio["semanas"]) == 1
    assert sum(grupo["series"] for grupo in mio["grupos"]) <= 1
    puntos = api.get("/api/progreso/evolucion/?clave=press inclinado").json()["puntos"]
    assert [punto["pesada"] for punto in puntos] == [30.0]


@pytest.mark.parametrize("url", ["/api/progreso/", "/api/progreso/evolucion/?clave=press inclinado"])
def test_sin_acceso_no_se_lee(anonimo, url):
    assert anonimo.get(url).status_code == 401


def test_con_contrasena_temporal_no_se_lee(api):
    api.cuenta.debe_cambiar_contrasena = True
    api.cuenta.save()

    assert api.get("/api/progreso/").status_code == 403
