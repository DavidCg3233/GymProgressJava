"""Cambiar la propia contraseña (T-006-12).

RNF-ACC-08: el usuario puede cambiar su contraseña escribiendo la actual.
RNF-ACC-09: quien entra con una contraseña temporal debe cambiarla.
RNF-SEG-10: la nueva cumple las mismas reglas que cualquier contraseña.
"""

import json

import pytest

from cuentas import servicios

from .conftest import CONTRASENA

pytestmark = pytest.mark.django_db

URL_ESTADO = "/api/acceso/"
URL_ENTRAR = "/api/acceso/entrar/"
URL_CONTRASENA = "/api/acceso/contrasena/"

NUEVA = "Zr7#pW4!nB"  # 10 caracteres


def enviar(client, url, **datos):
    return client.post(url, data=json.dumps(datos), content_type="application/json")


def entrar(client, contrasena=CONTRASENA):
    return enviar(client, URL_ENTRAR, identificador="davidc", contrasena=contrasena)


def cambiar(client, actual=CONTRASENA, nueva=NUEVA):
    return enviar(client, URL_CONTRASENA, actual=actual, nueva=nueva)


def test_con_la_contrasena_actual_correcta_se_cambia(client, cuenta):
    entrar(client)

    respuesta = cambiar(client)

    assert respuesta.status_code == 204
    cuenta.refresh_from_db()
    assert cuenta.check_password(NUEVA) is True
    assert cuenta.check_password(CONTRASENA) is False


def test_despues_de_cambiarla_se_sigue_dentro_en_este_navegador(client, cuenta):
    entrar(client)

    cambiar(client)

    assert client.get(URL_ESTADO).json()["autenticado"] is True


def test_despues_de_cambiarla_los_demas_navegadores_quedan_fuera(client, cuenta):
    from django.test import Client

    otro = Client()
    entrar(otro)
    entrar(client)

    cambiar(client)

    assert otro.get(URL_ESTADO).json()["autenticado"] is False


def test_con_la_contrasena_actual_equivocada_no_se_cambia(client, cuenta):
    entrar(client)

    respuesta = cambiar(client, actual="no-es-la-mia")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "La contraseña actual no es correcta."}
    cuenta.refresh_from_db()
    assert cuenta.check_password(CONTRASENA) is True


def test_sin_haber_entrado_no_se_puede_cambiar_ninguna_contrasena(client, cuenta):
    respuesta = cambiar(client)

    assert respuesta.status_code == 401
    cuenta.refresh_from_db()
    assert cuenta.check_password(CONTRASENA) is True


@pytest.mark.parametrize(
    ("nueva", "fragmento"),
    [
        pytest.param("Zr7#pW4!n", "10", id="RNF-SEG-10: 9 caracteres"),
        pytest.param("1234567890", "numérica", id="solo numeros"),
        pytest.param("davidc123!", "parecida", id="parecida al usuario"),
    ],
)
def test_la_nueva_contrasena_debe_cumplir_las_reglas(client, cuenta, nueva, fragmento):
    entrar(client)

    respuesta = cambiar(client, nueva=nueva)

    assert respuesta.status_code == 400
    assert fragmento in respuesta.json()["mensaje"]
    cuenta.refresh_from_db()
    assert cuenta.check_password(CONTRASENA) is True


def test_la_nueva_contrasena_debe_ser_distinta_de_la_actual(client, cuenta):
    entrar(client)

    respuesta = cambiar(client, nueva=CONTRASENA)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "La contraseña nueva debe ser distinta de la actual."}


@pytest.mark.parametrize("cuerpo", ["no es json", "[]", '{"actual": 1, "nueva": null}'])
def test_una_peticion_mal_formada_se_rechaza_sin_cambiar_nada(client, cuenta, cuerpo):
    entrar(client)

    respuesta = client.post(URL_CONTRASENA, data=cuerpo, content_type="application/json")

    assert respuesta.status_code == 400
    cuenta.refresh_from_db()
    assert cuenta.check_password(CONTRASENA) is True


# --- RNF-ACC-09: contraseña temporal ----------------------------------------


def test_al_entrar_con_una_temporal_el_servidor_avisa_que_hay_que_cambiarla(client, cuenta):
    temporal = servicios.restablecer_contrasena(cuenta)

    respuesta = entrar(client, temporal)

    assert respuesta.json()["cuenta"]["debe_cambiar_contrasena"] is True
    assert client.get(URL_ESTADO).json()["cuenta"]["debe_cambiar_contrasena"] is True


def test_al_cambiar_la_temporal_desaparece_el_aviso(client, cuenta):
    temporal = servicios.restablecer_contrasena(cuenta)
    entrar(client, temporal)

    assert cambiar(client, actual=temporal).status_code == 204

    assert client.get(URL_ESTADO).json()["cuenta"]["debe_cambiar_contrasena"] is False
