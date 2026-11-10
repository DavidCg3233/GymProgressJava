"""Entrar y salir (T-006-10).

RNF-ACC-01: se entra con correo o nombre de usuario, más la contraseña.
RNF-ACC-02 y 03: el acceso se recuerda 7 días, contados desde el último uso.
RNF-ACC-04: al salir no se ve ningún dato sin volver a entrar.
RNF-SEG-09 y RNF-USA-02: los errores no revelan detalles ni usan términos técnicos.
"""

import json

import pytest
from django.conf import settings
from django.test import Client

from .conftest import CONTRASENA

pytestmark = pytest.mark.django_db

URL_ESTADO = "/api/acceso/"
URL_ENTRAR = "/api/acceso/entrar/"
URL_SALIR = "/api/acceso/salir/"

MENSAJE_DE_RECHAZO = "Usuario o contraseña incorrectos."
SIETE_DIAS_EN_SEGUNDOS = 7 * 24 * 60 * 60


def entrar(client, identificador="davidc", contrasena=CONTRASENA):
    return client.post(
        URL_ENTRAR,
        data=json.dumps({"identificador": identificador, "contrasena": contrasena}),
        content_type="application/json",
    )


def esta_dentro(client) -> bool:
    return client.get(URL_ESTADO).json()["autenticado"]


# --- RNF-ACC-01: entrar con correo o con usuario ----------------------------


@pytest.mark.parametrize(
    "identificador",
    [
        pytest.param("davidc", id="con el nombre de usuario"),
        pytest.param("david@ejemplo.com", id="con el correo"),
        pytest.param("DavidC", id="usuario con otras mayusculas"),
        pytest.param("  DAVID@Ejemplo.com ", id="correo con mayusculas y espacios"),
    ],
)
def test_se_puede_entrar(client, cuenta, identificador):
    respuesta = entrar(client, identificador)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"cuenta": {"usuario": "davidc", "correo": "david@ejemplo.com", "nombre": "David"}}
    assert esta_dentro(client) is True


def test_la_respuesta_nunca_incluye_la_contrasena(client, cuenta):
    cuerpo = entrar(client).content.decode()

    assert "password" not in cuerpo
    assert "contrasena" not in cuerpo
    assert "argon2" not in cuerpo


# --- Rechazos: mismo mensaje siempre, para no revelar qué falló --------------


@pytest.mark.parametrize(
    ("identificador", "contrasena"),
    [
        pytest.param("davidc", "contrasena-equivocada", id="contrasena incorrecta"),
        pytest.param("no-existe", CONTRASENA, id="usuario que no existe"),
        pytest.param("nadie@ejemplo.com", CONTRASENA, id="correo que no existe"),
        pytest.param("", CONTRASENA, id="sin identificador"),
        pytest.param("davidc", "", id="sin contrasena"),
    ],
)
def test_un_intento_fallido_se_rechaza_sin_decir_que_fallo(client, cuenta, identificador, contrasena):
    respuesta = entrar(client, identificador, contrasena)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": MENSAJE_DE_RECHAZO}
    assert esta_dentro(client) is False


def test_una_cuenta_desactivada_no_puede_entrar_y_recibe_el_mismo_mensaje(client, cuenta):
    cuenta.is_active = False
    cuenta.save()

    respuesta = entrar(client)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": MENSAJE_DE_RECHAZO}


@pytest.mark.parametrize(
    "cuerpo",
    [
        pytest.param("esto no es json", id="texto que no es JSON"),
        pytest.param("[1, 2, 3]", id="JSON que no es un objeto"),
        pytest.param('{"identificador": 5, "contrasena": ["x"]}', id="tipos equivocados"),
    ],
)
def test_una_peticion_mal_formada_se_rechaza_sin_romper_el_servidor(client, cuenta, cuerpo):
    respuesta = client.post(URL_ENTRAR, data=cuerpo, content_type="application/json")

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": MENSAJE_DE_RECHAZO}


def test_entrar_solo_acepta_envios_no_consultas(client, cuenta):
    assert client.get(URL_ENTRAR).status_code == 405


# --- La cookie del acceso ---------------------------------------------------


def test_la_cookie_del_acceso_no_es_legible_por_codigo_y_solo_viaja_cifrada(client, cuenta):
    cookie = entrar(client).cookies[settings.SESSION_COOKIE_NAME]

    assert cookie["httponly"] is True  # código inyectado en la página no puede leerla
    assert cookie["secure"] is True  # solo viaja por HTTPS (RNF-SEG-02)
    assert cookie["samesite"] == "Lax"  # otros sitios no pueden usarla para enviar acciones
    assert int(cookie["max-age"]) == SIETE_DIAS_EN_SEGUNDOS


def test_al_entrar_se_estrena_identificador_de_sesion(client, cuenta):
    # Evita que alguien fije de antemano el identificador de la víctima.
    client.get(URL_ESTADO)
    antes = client.session.session_key

    entrar(client)

    assert client.session.session_key != antes


# --- RNF-ACC-02 y 03: 7 días desde el último uso ----------------------------


def test_usando_la_app_el_dia_6_y_el_12_no_se_vuelve_a_pedir_contrasena(client, cuenta, reloj):
    entrar(client)

    reloj.avanzar(days=6)
    assert esta_dentro(client) is True  # este uso renueva los 7 días

    reloj.avanzar(days=6)  # día 12 desde que se escribió la contraseña
    assert esta_dentro(client) is True


def test_tras_7_dias_sin_uso_se_pide_la_contrasena_otra_vez(client, cuenta, reloj):
    entrar(client)

    reloj.avanzar(days=7, seconds=1)

    assert esta_dentro(client) is False


def test_un_instante_antes_de_los_7_dias_el_acceso_sigue_vigente(client, cuenta, reloj):
    entrar(client)

    reloj.avanzar(days=6, hours=23, minutes=59)

    assert esta_dentro(client) is True


# --- RNF-ACC-04: salir ------------------------------------------------------


def test_al_salir_ya_no_se_esta_dentro(client, cuenta):
    entrar(client)

    respuesta = client.post(URL_SALIR)

    assert respuesta.status_code == 204
    assert esta_dentro(client) is False


def test_al_salir_la_sesion_anterior_queda_inservible(client, cuenta):
    entrar(client)
    cookie_anterior = client.cookies[settings.SESSION_COOKIE_NAME].value
    client.post(URL_SALIR)

    otro_navegador = Client()
    otro_navegador.cookies[settings.SESSION_COOKIE_NAME] = cookie_anterior

    assert esta_dentro(otro_navegador) is False


def test_salir_sin_haber_entrado_no_es_un_error(client):
    assert client.post(URL_SALIR).status_code == 204


def test_el_estado_sin_acceso_no_trae_datos_de_ninguna_cuenta(client, cuenta):
    assert client.get(URL_ESTADO).json() == {"autenticado": False, "cuenta": None}


def test_el_estado_con_acceso_trae_solo_los_datos_de_la_cuenta(client, cuenta):
    entrar(client)

    assert client.get(URL_ESTADO).json() == {
        "autenticado": True,
        "cuenta": {"usuario": "davidc", "correo": "david@ejemplo.com", "nombre": "David"},
    }


# --- Protección CSRF: otro sitio no puede enviar acciones a nombre del usuario


@pytest.fixture
def navegador_estricto():
    return Client(enforce_csrf_checks=True)


def test_entrar_sin_el_token_de_proteccion_se_rechaza(navegador_estricto, cuenta):
    assert entrar(navegador_estricto).status_code == 403


def test_consultar_el_estado_entrega_el_token_y_con_el_se_puede_entrar(navegador_estricto, cuenta):
    navegador_estricto.get(URL_ESTADO)
    token = navegador_estricto.cookies[settings.CSRF_COOKIE_NAME].value

    respuesta = navegador_estricto.post(
        URL_ENTRAR,
        data=json.dumps({"identificador": "davidc", "contrasena": CONTRASENA}),
        content_type="application/json",
        headers={"X-CSRFToken": token},
    )

    assert respuesta.status_code == 200


def test_salir_sin_el_token_de_proteccion_se_rechaza(navegador_estricto, cuenta):
    assert navegador_estricto.post(URL_SALIR).status_code == 403
