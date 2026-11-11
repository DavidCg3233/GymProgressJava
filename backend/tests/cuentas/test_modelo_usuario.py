"""Modelo de cuenta (T-006-09).

RNF-ACC-10: de cada cuenta se guardan solo nombre para mostrar, nombre de
usuario (único), correo (único) y contraseña.
RNF-SEG-01: ninguna contraseña se guarda de forma legible.
RNF-SEG-10: contraseña de mínimo 10 caracteres.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

pytestmark = pytest.mark.django_db

CONTRASENA_VALIDA = "Xk9!mQ2#vL"  # 10 caracteres


def crear(**cambios):
    datos = {
        "usuario": "davidc",
        "correo": "david@ejemplo.com",
        "nombre": "David",
        "password": CONTRASENA_VALIDA,
    }
    datos.update(cambios)
    return get_user_model().objects.create_user(**datos)


# --- RNF-ACC-10: qué se guarda de una cuenta --------------------------------


def test_una_cuenta_guarda_nombre_usuario_y_correo():
    cuenta = crear()

    cuenta.refresh_from_db()
    assert (cuenta.nombre, cuenta.usuario, cuenta.correo) == ("David", "davidc", "david@ejemplo.com")


def test_la_cuenta_no_tiene_campos_personales_de_mas():
    # La v1.0 pedía dos nombres, dos apellidos, sexo y fecha de nacimiento sin usarlos.
    campos = {campo.name for campo in get_user_model()._meta.get_fields() if not campo.is_relation}

    assert campos == {
        "id",
        "usuario",
        "correo",
        "nombre",
        "debe_cambiar_contrasena",
        "password",
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "creada",
        "meta_semanal",  # RF-004-11: una preferencia, no un dato personal.
    }


def test_una_cuenta_nueva_esta_activa_y_no_es_administradora():
    cuenta = crear()

    assert cuenta.is_active is True
    assert cuenta.is_staff is False
    assert cuenta.is_superuser is False


@pytest.mark.parametrize("campo", ["usuario", "correo", "nombre"])
def test_usuario_correo_y_nombre_son_obligatorios(campo):
    with pytest.raises(ValueError, match=campo):
        crear(**{campo: "  "})


def test_el_correo_y_el_usuario_se_guardan_en_minusculas_y_sin_espacios():
    cuenta = crear(usuario="  DavidC ", correo=" David@Ejemplo.COM ")

    assert cuenta.usuario == "davidc"
    assert cuenta.correo == "david@ejemplo.com"


def test_el_nombre_conserva_las_mayusculas_que_escribio_la_persona():
    assert crear(nombre="  David Fernando ").nombre == "David Fernando"


# --- Unicidad ---------------------------------------------------------------


@pytest.mark.parametrize("correo", ["david@ejemplo.com", "DAVID@ejemplo.com"])
def test_no_puede_haber_dos_cuentas_con_el_mismo_correo(correo):
    crear()

    with pytest.raises(IntegrityError), transaction.atomic():
        crear(usuario="otro", correo=correo)


@pytest.mark.parametrize("usuario", ["davidc", "DavidC"])
def test_no_puede_haber_dos_cuentas_con_el_mismo_usuario(usuario):
    crear()

    with pytest.raises(IntegrityError), transaction.atomic():
        crear(usuario=usuario, correo="otro@ejemplo.com")


def test_la_base_tambien_impide_duplicados_que_solo_cambian_mayusculas():
    # Defensa en profundidad: aunque alguien se salte el normalizado, la base lo rechaza.
    Usuario = get_user_model()
    crear()

    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.bulk_create(
            [Usuario(usuario="DAVIDC", correo="otro@ejemplo.com", nombre="Otro", password="x")]
        )


# --- RNF-SEG-01: la contraseña no se guarda legible --------------------------


def test_la_contrasena_no_se_guarda_en_texto_legible():
    cuenta = crear()

    assert CONTRASENA_VALIDA not in cuenta.password
    assert cuenta.check_password(CONTRASENA_VALIDA) is True
    assert cuenta.check_password("otra-contrasena") is False


def test_la_contrasena_se_cifra_con_argon2():
    assert crear().password.startswith("argon2")


def test_dos_cuentas_con_la_misma_contrasena_guardan_valores_distintos():
    primera = crear()
    segunda = crear(usuario="otro", correo="otro@ejemplo.com")

    assert primera.password != segunda.password


# --- RNF-SEG-10: mínimo 10 caracteres ---------------------------------------


def test_una_contrasena_de_9_caracteres_se_rechaza():
    with pytest.raises(ValidationError) as error:
        validate_password("Xk9!mQ2#v")

    assert "10" in " ".join(error.value.messages)


def test_una_contrasena_de_10_caracteres_se_acepta():
    validate_password(CONTRASENA_VALIDA)


@pytest.mark.parametrize(
    "contrasena",
    [
        pytest.param("1234567890", id="solo numeros"),
        pytest.param("password123", id="de las mas comunes"),
    ],
)
def test_una_contrasena_larga_pero_adivinable_se_rechaza(contrasena):
    with pytest.raises(ValidationError):
        validate_password(contrasena)


def test_una_contrasena_parecida_al_usuario_se_rechaza():
    cuenta = get_user_model()(usuario="davidcalambas", correo="d@ejemplo.com", nombre="David")

    with pytest.raises(ValidationError):
        validate_password("davidcalambas1", user=cuenta)
