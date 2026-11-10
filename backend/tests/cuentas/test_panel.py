"""Panel del dueño para administrar cuentas (T-006-12).

RNF-ACC-05 y RNF-ACC-09: el dueño crea cuentas y restablece contraseñas
desde el panel de administración; nadie más puede.
"""

import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from cuentas import servicios

from .conftest import CONTRASENA

pytestmark = pytest.mark.django_db

URL_LISTA = "/panel/cuentas/usuario/"
URL_NUEVA = "/panel/cuentas/usuario/add/"
BACKEND = "cuentas.autenticacion.UsuarioOCorreo"


@pytest.fixture
def dueno(db):
    return get_user_model().objects.create_superuser(
        usuario="dueno", correo="dueno@ejemplo.com", nombre="Dueño", password=CONTRASENA
    )


@pytest.fixture
def panel(client, dueno):
    client.force_login(dueno, backend=BACKEND)
    return client


def mensajes_de(respuesta) -> str:
    return " ".join(str(mensaje) for mensaje in get_messages(respuesta.wsgi_request))


def contrasena_en(texto: str) -> str:
    """Extrae la contraseña temporal del mensaje que ve el dueño."""
    return re.search(r"Contraseña temporal: (\S+)", texto).group(1)


DATOS = {"usuario": "andrea", "correo": "andrea@ejemplo.com", "nombre": "Andrea"}


# --- Quién puede entrar al panel --------------------------------------------


def test_sin_acceso_el_panel_manda_a_identificarse(client):
    respuesta = client.get(URL_LISTA)

    assert respuesta.status_code == 302
    assert "/panel/login/" in respuesta["Location"]


def test_una_cuenta_normal_no_puede_entrar_al_panel(client, cuenta):
    client.force_login(cuenta, backend=BACKEND)

    respuesta = client.get(URL_LISTA)

    assert respuesta.status_code == 302
    assert "/panel/login/" in respuesta["Location"]


def test_el_dueno_ve_la_lista_de_cuentas(panel, cuenta):
    respuesta = panel.get(URL_LISTA)

    assert respuesta.status_code == 200
    assert "davidc" in respuesta.content.decode()


# --- Crear una cuenta -------------------------------------------------------


def test_el_formulario_para_crear_no_pide_contrasena(panel):
    pagina = panel.get(URL_NUEVA).content.decode()

    assert 'name="usuario"' in pagina
    assert 'name="correo"' in pagina
    assert 'name="nombre"' in pagina
    assert 'type="password"' not in pagina


def test_el_dueno_crea_una_cuenta_y_ve_su_contrasena_temporal_una_vez(panel):
    respuesta = panel.post(URL_NUEVA, DATOS)

    assert respuesta.status_code == 302
    creada = get_user_model().objects.get(usuario="andrea")
    temporal = contrasena_en(mensajes_de(respuesta))
    assert creada.check_password(temporal) is True
    assert creada.debe_cambiar_contrasena is True
    assert creada.is_staff is False


def test_la_sexta_cuenta_se_rechaza_con_un_mensaje_claro(panel):
    for numero in range(1, 5):  # con el dueño ya son 5
        servicios.invitar(usuario=f"p{numero}", correo=f"p{numero}@ejemplo.com", nombre=f"P {numero}")

    respuesta = panel.post(URL_NUEVA, DATOS)

    assert respuesta.status_code == 200  # vuelve a mostrar el formulario con el error
    assert "máximo de 5 cuentas" in respuesta.content.decode()
    assert not get_user_model().objects.filter(usuario="andrea").exists()


def test_un_correo_repetido_se_rechaza_en_el_formulario(panel, cuenta):
    respuesta = panel.post(URL_NUEVA, {**DATOS, "correo": "DAVID@ejemplo.com"})

    assert respuesta.status_code == 200
    assert not get_user_model().objects.filter(usuario="andrea").exists()


# --- Restablecer una contraseña ---------------------------------------------


def test_el_dueno_restablece_la_contrasena_de_una_cuenta(panel, cuenta):
    respuesta = panel.post(
        URL_LISTA,
        {"action": "restablecer_contrasena", "_selected_action": [cuenta.pk]},
    )

    cuenta.refresh_from_db()
    temporal = contrasena_en(mensajes_de(respuesta))
    assert cuenta.check_password(temporal) is True
    assert cuenta.check_password(CONTRASENA) is False
    assert cuenta.debe_cambiar_contrasena is True


def test_el_panel_nunca_muestra_la_contrasena_cifrada(panel, cuenta):
    pagina = panel.get(f"{URL_LISTA}{cuenta.pk}/change/").content.decode()

    assert "argon2" not in pagina
