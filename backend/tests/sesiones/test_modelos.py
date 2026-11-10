"""La base de datos defiende los datos por sí sola (T-006-17).

Estas pruebas se saltan los servicios y escriben directo en la base, para
comprobar que las restricciones existen aunque el código tuviera un error.
"""

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from sesiones.models import Serie, Sesion, SesionEjercicio

from .conftest import crear_cuenta

pytestmark = pytest.mark.django_db


@pytest.fixture
def ejercicio(db):
    sesion = Sesion.objects.create(id=uuid.uuid4(), usuario=crear_cuenta(), nombre="Pecho", inicio=timezone.now())
    return SesionEjercicio.objects.create(
        id=uuid.uuid4(), sesion=sesion, nombre="Press inclinado", clave="press inclinado", grupo="Pecho", orden=1
    )


def serie(ejercicio, **cambios):
    datos = {"numero": 1, "peso": Decimal("30"), "reps": 10, "confirmada": True} | cambios
    return Serie.objects.create(id=uuid.uuid4(), ejercicio=ejercicio, **datos)


@pytest.mark.parametrize(
    "cambios",
    [
        pytest.param({"peso": Decimal("500.5")}, id="peso sobre el maximo"),
        pytest.param({"peso": Decimal("-0.5")}, id="peso negativo"),
        pytest.param({"reps": 0}, id="cero repeticiones"),
        pytest.param({"reps": 101}, id="repeticiones sobre el maximo"),
        pytest.param({"numero": 0}, id="serie numero cero"),
        pytest.param({"numero": 11}, id="serie numero once"),
    ],
)
def test_la_base_rechaza_una_serie_fuera_de_rango(ejercicio, cambios):
    with pytest.raises(IntegrityError), transaction.atomic():
        serie(ejercicio, **cambios)


def test_la_base_rechaza_dos_series_con_el_mismo_numero(ejercicio):
    serie(ejercicio, numero=1)

    with pytest.raises(IntegrityError), transaction.atomic():
        serie(ejercicio, numero=1)


def test_la_base_rechaza_una_segunda_sesion_en_curso_de_la_misma_persona(ejercicio):
    usuario = ejercicio.sesion.usuario

    with pytest.raises(IntegrityError), transaction.atomic():
        Sesion.objects.create(id=uuid.uuid4(), usuario=usuario, nombre="Otra", inicio=timezone.now())


def test_la_base_permite_muchas_sesiones_terminadas(ejercicio):
    usuario = ejercicio.sesion.usuario
    ayer = timezone.now() - timedelta(days=1)

    for _ in range(3):
        Sesion.objects.create(
            id=uuid.uuid4(), usuario=usuario, nombre="Vieja", inicio=ayer, fin=ayer + timedelta(hours=1)
        )

    assert Sesion.objects.filter(usuario=usuario).count() == 4


def test_la_base_rechaza_una_sesion_que_termina_antes_de_empezar(db):
    ahora = timezone.now()

    with pytest.raises(IntegrityError), transaction.atomic():
        Sesion.objects.create(
            id=uuid.uuid4(), usuario=crear_cuenta(), nombre="Rara", inicio=ahora, fin=ahora - timedelta(minutes=1)
        )


def test_al_eliminar_una_sesion_se_van_sus_ejercicios_y_series(ejercicio):
    serie(ejercicio)

    ejercicio.sesion.delete()

    assert SesionEjercicio.objects.count() == 0
    assert Serie.objects.count() == 0


def test_al_eliminar_una_cuenta_se_van_sus_sesiones(ejercicio):
    ejercicio.sesion.usuario.delete()

    assert Sesion.objects.count() == 0
