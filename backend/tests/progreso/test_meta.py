"""Meta semanal de sesiones (T-004-03).

Spec 004 · RF-004-11 · RN-004-08.
"""

import pytest
from django.db import IntegrityError, transaction

pytestmark = pytest.mark.django_db

URL = "/api/progreso/meta/"


def test_fijar_cambiar_y_quitar_la_meta(api):
    assert api.put(URL, meta=4).json() == {"meta": 4}
    api.cuenta.refresh_from_db()
    assert api.cuenta.meta_semanal == 4

    assert api.put(URL, meta=5).json() == {"meta": 5}
    assert api.put(URL, meta=None).json() == {"meta": None}
    api.cuenta.refresh_from_db()
    assert api.cuenta.meta_semanal is None


def test_una_cuenta_nueva_no_tiene_meta(cuenta):
    assert cuenta.meta_semanal is None


@pytest.mark.parametrize("valor", [0, 15, "4", 2.5, True])
def test_meta_fuera_de_rango_se_rechaza(api, valor):
    respuesta = api.put(URL, meta=valor)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "La meta va de 1 a 14 sesiones por semana.", "campo": "meta"}


def test_sin_el_campo_meta_se_rechaza(api):
    assert api.put(URL).status_code == 400


def test_la_meta_es_de_cada_cuenta(api, otra):
    api.put(URL, meta=4)

    otra.cuenta.refresh_from_db()
    assert otra.cuenta.meta_semanal is None


def test_sin_acceso_no_se_puede_fijar(anonimo):
    assert anonimo.put(URL, meta=4).status_code == 401


@pytest.mark.parametrize("valor", [0, 15])
def test_la_base_rechaza_una_meta_fuera_de_rango(cuenta, valor):
    cuenta.meta_semanal = valor
    with pytest.raises(IntegrityError), transaction.atomic():
        cuenta.save(update_fields=["meta_semanal"])
