"""Entradas mal formadas no rompen el servidor (RNF-SEG-04, RNF-SEG-09).

Un dato inesperado debe terminar en un rechazo claro, nunca en un error interno.
"""

import pytest

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("ejercicio", ["no-es-un-uuid", 123, None, "", ["x"], {"a": 1}])
def test_una_serie_con_un_identificador_de_ejercicio_invalido_no_existe(api, ahora, ejercicio):
    respuesta = api.put(
        f"/api/series/{nuevo_id()}/", ejercicio=ejercicio, numero=1, peso=30, reps=10, confirmada=True
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize("cuerpo", ["esto no es json", "[1, 2]", '"texto"', "null", ""])
def test_un_cuerpo_que_no_es_un_objeto_json_se_rechaza(api, cuerpo):
    respuesta = api.client.put(f"/api/sesiones/{nuevo_id()}/", data=cuerpo, content_type="application/json")

    assert respuesta.status_code == 400
    assert "mensaje" in respuesta.json()


def test_un_cuerpo_que_no_es_json_se_rechaza(api):
    respuesta = api.client.put(f"/api/sesiones/{nuevo_id()}/", data="a=1", content_type="text/plain")

    assert respuesta.status_code in (400, 415)
    assert "mensaje" in respuesta.json()


@pytest.mark.parametrize("campo", ["nombre", "nota"])
@pytest.mark.parametrize("valor", [123, ["x"], {"a": 1}, True])
def test_un_texto_con_tipo_equivocado_se_rechaza(api, ahora, campo, valor):
    datos = {"nombre": "", "inicio": ahora.isoformat(), "fin": None, "nota": ""} | {campo: valor}

    respuesta = api.put(f"/api/sesiones/{nuevo_id()}/", **datos)

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == campo


def test_un_metodo_no_permitido_responde_con_mensaje(api):
    respuesta = api.client.post("/api/arranque/", data="{}", content_type="application/json")

    assert respuesta.status_code == 405
    assert "mensaje" in respuesta.json()
