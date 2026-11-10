"""Cuentas por invitación (T-006-12).

RNF-ACC-05: solo el dueño crea cuentas; máximo 5 en total.
RNF-ACC-09: si alguien olvida la contraseña, el dueño le genera una temporal
            que debe cambiar al entrar. No hay correo de recuperación.
RNF-PLA-04: no existe registro público.
"""

import pytest
from django.contrib.auth import authenticate, get_user_model

from cuentas import servicios
from cuentas.models import MAXIMO_DE_CUENTAS, LimiteDeCuentasAlcanzado

pytestmark = pytest.mark.django_db


def invitar(numero=1):
    return servicios.invitar(usuario=f"persona{numero}", correo=f"persona{numero}@ejemplo.com", nombre=f"Persona {numero}")


# --- Invitar ----------------------------------------------------------------


def test_invitar_crea_la_cuenta_y_entrega_una_contrasena_temporal(rf):
    cuenta, temporal = invitar()

    assert cuenta.usuario == "persona1"
    assert cuenta.check_password(temporal) is True
    assert authenticate(rf.post("/api/acceso/entrar/"), username="persona1", password=temporal) == cuenta


def test_la_cuenta_invitada_debe_cambiar_la_contrasena_al_entrar():
    cuenta, _ = invitar()

    assert cuenta.debe_cambiar_contrasena is True


def test_una_cuenta_creada_con_su_propia_contrasena_no_esta_obligada_a_cambiarla(cuenta):
    assert cuenta.debe_cambiar_contrasena is False


def test_la_contrasena_temporal_es_larga_y_distinta_cada_vez():
    _, primera = invitar(1)
    _, segunda = invitar(2)

    assert len(primera) >= 16
    assert primera != segunda


def test_la_cuenta_invitada_no_es_administradora():
    cuenta, _ = invitar()

    assert cuenta.is_staff is False
    assert cuenta.is_superuser is False


# --- RNF-ACC-05: máximo 5 cuentas -------------------------------------------


def test_el_tope_es_de_5_cuentas():
    assert MAXIMO_DE_CUENTAS == 5


def test_se_pueden_crear_5_cuentas():
    for numero in range(1, 6):
        invitar(numero)

    assert get_user_model().objects.count() == 5


def test_la_sexta_cuenta_se_rechaza():
    for numero in range(1, 6):
        invitar(numero)

    with pytest.raises(LimiteDeCuentasAlcanzado, match="5"):
        invitar(6)

    assert get_user_model().objects.count() == 5


def test_el_tope_cuenta_tambien_la_cuenta_del_dueno(cuenta):
    for numero in range(1, 5):
        invitar(numero)

    with pytest.raises(LimiteDeCuentasAlcanzado):
        invitar(5)


def test_modificar_una_cuenta_existente_no_choca_con_el_tope():
    cuentas = [invitar(numero)[0] for numero in range(1, 6)]

    cuentas[0].nombre = "Otro nombre"
    cuentas[0].save()

    assert get_user_model().objects.get(pk=cuentas[0].pk).nombre == "Otro nombre"


def test_al_eliminar_una_cuenta_se_libera_un_cupo():
    cuentas = [invitar(numero)[0] for numero in range(1, 6)]

    cuentas[0].delete()

    assert invitar(6)[0].usuario == "persona6"


# --- RNF-ACC-09: restablecer ------------------------------------------------


def test_restablecer_cambia_la_contrasena_y_obliga_a_cambiarla(cuenta):
    from .conftest import CONTRASENA

    temporal = servicios.restablecer_contrasena(cuenta)

    cuenta.refresh_from_db()
    assert cuenta.check_password(temporal) is True
    assert cuenta.check_password(CONTRASENA) is False
    assert cuenta.debe_cambiar_contrasena is True


# --- RNF-PLA-04: sin registro público ---------------------------------------


@pytest.mark.parametrize(
    "ruta",
    ["/api/acceso/registro/", "/api/acceso/registrar/", "/api/registro/", "/registro/", "/signup/", "/api/acceso/recuperar/"],
)
def test_no_existe_ninguna_ruta_publica_para_crear_o_recuperar_cuentas(client, ruta):
    assert client.post(ruta).status_code == 404
    assert client.get(ruta).status_code == 404
