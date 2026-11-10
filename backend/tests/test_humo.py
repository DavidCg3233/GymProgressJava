"""Prueba de humo: el proyecto arranca y responde (T-006-02)."""

from django.conf import settings


def test_el_servidor_responde_que_esta_vivo(client):
    respuesta = client.get("/salud/")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_la_depuracion_esta_apagada_por_defecto():
    # RNF-SEG-08 y RNF-SEG-09: sin trazas internas hacia el usuario.
    assert settings.DEBUG is False


def test_la_interfaz_esta_en_espanol_y_hora_de_colombia():
    # RNF-USA-05.
    assert settings.LANGUAGE_CODE == "es-co"
    assert settings.TIME_ZONE == "America/Bogota"
    assert settings.USE_TZ is True
