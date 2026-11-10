"""Bloqueo por intentos fallidos (T-006-11).

RNF-ACC-07: tras 5 contraseñas incorrectas seguidas, el acceso a esa cuenta
se bloquea 15 minutos. El sexto intento se rechaza aunque sea correcto.
"""

import json

import pytest
from django.contrib.auth import get_user_model

from .conftest import CONTRASENA

pytestmark = pytest.mark.django_db

URL_ENTRAR = "/api/acceso/entrar/"
MENSAJE_DE_BLOQUEO = "Demasiados intentos. Espera 15 minutos e inténtalo de nuevo."


def entrar(client, identificador="davidc", contrasena=CONTRASENA):
    return client.post(
        URL_ENTRAR,
        data=json.dumps({"identificador": identificador, "contrasena": contrasena}),
        content_type="application/json",
    )


def fallar(client, veces, identificador="davidc"):
    for _ in range(veces):
        entrar(client, identificador, "contrasena-equivocada")


def test_el_sexto_intento_se_rechaza_aunque_la_contrasena_sea_correcta(client, cuenta):
    fallar(client, 5)

    respuesta = entrar(client)

    assert respuesta.status_code == 429
    assert respuesta.json() == {"mensaje": MENSAJE_DE_BLOQUEO}


def test_con_4_fallos_todavia_se_puede_entrar(client, cuenta):
    fallar(client, 4)

    assert entrar(client).status_code == 200


def test_entrar_bien_reinicia_la_cuenta_de_fallos(client, cuenta):
    fallar(client, 4)
    entrar(client)
    fallar(client, 4)

    assert entrar(client).status_code == 200


def test_pasados_15_minutos_se_puede_entrar_de_nuevo(client, cuenta, reloj):
    fallar(client, 5)

    reloj.avanzar(minutes=15, seconds=1)

    assert entrar(client).status_code == 200


def test_un_minuto_antes_de_los_15_sigue_bloqueada(client, cuenta, reloj):
    fallar(client, 5)

    reloj.avanzar(minutes=14)

    assert entrar(client).status_code == 429


@pytest.mark.parametrize(
    "variantes",
    [
        pytest.param(["davidc", "DavidC", " DAVIDC ", "davidc", "Davidc"], id="cambiando mayusculas y espacios"),
        pytest.param(["davidc", "david@ejemplo.com", "davidc", "DAVID@ejemplo.com", "davidc"], id="alternando usuario y correo"),
    ],
)
def test_el_bloqueo_no_se_evade_escribiendo_el_identificador_de_otra_forma(client, cuenta, variantes):
    for identificador in variantes:
        entrar(client, identificador, "contrasena-equivocada")

    assert entrar(client).status_code == 429
    assert entrar(client, "david@ejemplo.com").status_code == 429


def test_el_bloqueo_de_una_cuenta_no_afecta_a_otra(client, cuenta):
    get_user_model().objects.create_user(
        usuario="andrea", correo="andrea@ejemplo.com", nombre="Andrea", password=CONTRASENA
    )
    fallar(client, 5)

    assert entrar(client, "andrea").status_code == 200


def test_un_identificador_que_no_existe_se_bloquea_igual(client, cuenta):
    # Si solo se bloquearan las cuentas reales, el bloqueo revelaría cuáles existen.
    fallar(client, 5, identificador="no-existe")

    respuesta = entrar(client, "no-existe", "lo-que-sea")

    assert respuesta.status_code == 429
    assert respuesta.json() == {"mensaje": MENSAJE_DE_BLOQUEO}


def test_el_bloqueo_sigue_a_la_cuenta_aunque_se_intente_desde_otro_navegador(client, cuenta):
    from django.test import Client

    fallar(client, 5)

    assert entrar(Client()).status_code == 429
