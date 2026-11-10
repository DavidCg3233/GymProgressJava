"""Quién puede usar la API de sesiones (T-006-13).

RNF-ACC-06 y RNF-SEG-06: cada persona ve y modifica únicamente lo suyo; el
servidor lo comprueba en cada operación.
RNF-ACC-09: con una contraseña temporal no se usa la app hasta cambiarla.
"""

from datetime import timedelta

import pytest

from cuentas import servicios

from .conftest import Api, nuevo_id

pytestmark = pytest.mark.django_db


@pytest.fixture
def de_david(api, ahora):
    """Una sesión terminada y otra en curso de David, con sus identificadores."""
    inicio = ahora - timedelta(days=1)
    terminada = api.sesion_terminada([(30, 10)], inicio=inicio)
    en_curso = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(en_curso)
    serie = api.serie(ejercicio)
    return {"terminada": terminada, "en_curso": en_curso, "ejercicio": ejercicio, "serie": serie}


def operaciones(ids, ahora):
    """Toda operación de la API sobre datos ya existentes: (método, url, cuerpo)."""
    sesion = {"nombre": "", "inicio": ahora.isoformat(), "fin": None, "nota": ""}
    ejercicio = {"nombre": "Fondos", "grupo": "Pecho", "orden": 2, "nota": ""}
    serie = {"ejercicio": ids["ejercicio"], "numero": 1, "peso": 99, "reps": 1, "confirmada": True}
    return [
        ("get", f"/api/sesiones/{ids['terminada']}/", {}),
        ("get", f"/api/sesiones/{ids['en_curso']}/", {}),
        ("put", f"/api/sesiones/{ids['en_curso']}/", sesion),
        ("delete", f"/api/sesiones/{ids['terminada']}/", {}),
        ("put", f"/api/sesiones/{ids['en_curso']}/ejercicios/{ids['ejercicio']}/", ejercicio),
        ("put", f"/api/sesiones/{ids['en_curso']}/ejercicios/{nuevo_id()}/", ejercicio),
        ("put", f"/api/series/{ids['serie']}/", serie),
        ("put", f"/api/series/{nuevo_id()}/", serie | {"numero": 2}),
        ("delete", f"/api/series/{ids['serie']}/", {}),
    ]


def llamar(api, metodo, url, cuerpo):
    return getattr(api, metodo)(url, **cuerpo) if metodo != "get" else api.get(url)


# --- Sin acceso -------------------------------------------------------------


def test_sin_acceso_ninguna_operacion_responde_datos(anonimo, de_david, ahora):
    todas = operaciones(de_david, ahora) + [("get", "/api/sesiones/", {}), ("get", "/api/arranque/", {})]

    for metodo, url, cuerpo in todas:
        respuesta = llamar(anonimo, metodo, url, cuerpo)

        assert respuesta.status_code == 401, (metodo, url)
        assert respuesta.json() == {"mensaje": "Entra con tu cuenta para continuar."}


# --- RNF-ACC-06: lo ajeno no existe para mí ---------------------------------


def test_otra_persona_no_puede_ver_ni_tocar_nada_de_david(api, otra, de_david, ahora):
    for metodo, url, cuerpo in operaciones(de_david, ahora):
        respuesta = llamar(otra, metodo, url, cuerpo)

        # 404 y no 403: ni siquiera se confirma que ese dato exista.
        assert respuesta.status_code == 404, (metodo, url)

    # Y nada de David cambió.
    assert api.get(f"/api/sesiones/{de_david['terminada']}/").status_code == 200
    intacta = api.get(f"/api/sesiones/{de_david['en_curso']}/").json()["sesion"]
    assert [(e["nombre"], [(s["peso"], s["reps"]) for s in e["series"]]) for e in intacta["ejercicios"]] == [
        ("Press inclinado", [(30.0, 10)])
    ]


def test_cada_persona_ve_solo_su_historial_y_su_arranque(api, otra, de_david, ahora):
    otra.sesion_terminada([(60, 5)], inicio=ahora - timedelta(days=2), ejercicio="Sentadilla", grupo="Pierna")

    assert [s["id"] for s in api.get("/api/sesiones/").json()["sesiones"]] == [de_david["terminada"]]
    assert list(api.get("/api/arranque/").json()["ultima_vez"]) == ["press inclinado"]
    assert list(otra.get("/api/arranque/").json()["ultima_vez"]) == ["sentadilla"]
    assert otra.get("/api/arranque/").json()["sesion_en_curso"] is None


def test_no_se_puede_ocupar_el_identificador_de_una_sesion_ajena(otra, de_david, ahora):
    respuesta = otra.put(
        f"/api/sesiones/{de_david['terminada']}/", nombre="mía", inicio=ahora.isoformat(), fin=None, nota=""
    )

    assert respuesta.status_code == 404


# --- RNF-ACC-09: contraseña temporal ----------------------------------------


def test_con_contrasena_temporal_la_api_no_responde_hasta_cambiarla(cuenta, ahora):
    servicios.restablecer_contrasena(cuenta)
    cuenta.refresh_from_db()
    api = Api(cuenta)

    respuesta = api.get("/api/arranque/")

    assert respuesta.status_code == 403
    assert respuesta.json() == {"mensaje": "Cambia tu contraseña temporal para continuar."}
    assert api.put(f"/api/sesiones/{nuevo_id()}/", nombre="", inicio=ahora.isoformat(), fin=None, nota="").status_code == 403


def test_tras_cambiar_la_temporal_la_api_responde(cuenta):
    temporal = servicios.restablecer_contrasena(cuenta)
    servicios.cambiar_contrasena(cuenta, temporal, "Zr7#pW4!nB")
    cuenta.refresh_from_db()

    assert Api(cuenta).get("/api/arranque/").status_code == 200


# --- Protección CSRF también en la API --------------------------------------


def test_la_api_rechaza_escrituras_sin_el_token_de_proteccion(cuenta, ahora):
    import json

    from django.test import Client

    from .conftest import BACKEND

    estricto = Client(enforce_csrf_checks=True)
    estricto.force_login(cuenta, backend=BACKEND)

    respuesta = estricto.put(
        f"/api/sesiones/{nuevo_id()}/",
        data=json.dumps({"nombre": "", "inicio": ahora.isoformat(), "fin": None, "nota": ""}),
        content_type="application/json",
    )

    assert respuesta.status_code == 403
