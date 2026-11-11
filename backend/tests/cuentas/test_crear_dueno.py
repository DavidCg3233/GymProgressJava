"""Crear la cuenta del dueño al publicar la app (RNF-ACC-05, RNF-ACC-09).

En Railway no hay una terminal a mano para correr `createsuperuser`. Este
comando corre en cada arranque: si no existe ninguna cuenta de dueño y están
las variables, la crea con una contraseña temporal que hay que cambiar al
entrar. Nunca escribe la contraseña en los registros (RNF-SEG-08) y nunca
detiene el arranque de la app.
"""

from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

pytestmark = pytest.mark.django_db

TEMPORAL = "Temporal-de-prueba-2026"
VARIABLES = {
    "GP_DUENO_USUARIO": "davidc",
    "GP_DUENO_CORREO": "david@ejemplo.com",
    "GP_DUENO_NOMBRE": "David",
    "GP_DUENO_CONTRASENA_TEMPORAL": TEMPORAL,
}


@pytest.fixture
def con_variables(monkeypatch):
    for nombre, valor in VARIABLES.items():
        monkeypatch.setenv(nombre, valor)


@pytest.fixture
def sin_variables(monkeypatch):
    for nombre in VARIABLES:
        monkeypatch.delenv(nombre, raising=False)


def correr() -> str:
    salida = StringIO()
    call_command("crear_dueno", stdout=salida)
    return salida.getvalue()


def test_con_las_variables_crea_la_cuenta_del_dueno(con_variables):
    correr()

    dueno = get_user_model().objects.get(usuario="davidc")
    assert (dueno.correo, dueno.nombre) == ("david@ejemplo.com", "David")
    assert dueno.is_superuser is True
    assert dueno.is_staff is True


def test_la_contrasena_es_temporal_y_hay_que_cambiarla_al_entrar(con_variables):
    correr()

    dueno = get_user_model().objects.get(usuario="davidc")
    assert dueno.check_password(TEMPORAL) is True
    assert dueno.debe_cambiar_contrasena is True


def test_nunca_escribe_la_contrasena_en_los_registros(con_variables):
    salida = correr()

    assert TEMPORAL not in salida
    assert "davidc" in salida


def test_si_ya_hay_un_dueno_no_hace_nada_aunque_cambien_las_variables(con_variables, monkeypatch):
    correr()
    dueno = get_user_model().objects.get(usuario="davidc")
    dueno.set_password("Mi-contrasena-definitiva-1")
    dueno.debe_cambiar_contrasena = False
    dueno.save()

    monkeypatch.setenv("GP_DUENO_CONTRASENA_TEMPORAL", "Otra-temporal-distinta-9")
    salida = correr()

    dueno.refresh_from_db()
    assert dueno.check_password("Mi-contrasena-definitiva-1") is True
    assert get_user_model().objects.count() == 1
    assert "ya existe" in salida.lower()


def test_sin_las_variables_no_crea_nada_y_lo_avisa(sin_variables):
    salida = correr()

    assert get_user_model().objects.count() == 0
    assert "GP_DUENO_USUARIO" in salida


def test_si_falta_una_variable_dice_cual(con_variables, monkeypatch):
    monkeypatch.delenv("GP_DUENO_CORREO")

    salida = correr()

    assert get_user_model().objects.count() == 0
    assert "GP_DUENO_CORREO" in salida


def test_una_contrasena_temporal_debil_se_rechaza_sin_detener_el_arranque(con_variables, monkeypatch):
    monkeypatch.setenv("GP_DUENO_CONTRASENA_TEMPORAL", "123")

    salida = correr()  # no lanza error

    assert get_user_model().objects.count() == 0
    assert "10" in salida
    assert "123" not in salida.replace("10", "")


def test_si_ya_hay_5_cuentas_no_puede_crearla_y_lo_avisa(con_variables):
    for numero in range(5):
        get_user_model().objects.create_user(
            usuario=f"p{numero}", correo=f"p{numero}@ejemplo.com", nombre="P", password="Xk9!mQ2#vL"
        )

    salida = correr()

    assert not get_user_model().objects.filter(usuario="davidc").exists()
    assert "5" in salida
