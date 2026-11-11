"""La base de datos defiende el peso corporal por sí sola (T-003-03).

Escriben directo en la base, saltándose los servicios.
Spec 003 · RN-003-03, 04, 06, 07 · plan 003, sección 4.1.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from cuerpo.models import RegistroDePeso

from .conftest import crear_cuenta

pytestmark = pytest.mark.django_db

HOY = date(2026, 11, 11)


@pytest.fixture
def david(db):
    return crear_cuenta()


def registrar(cuenta, peso, fecha=HOY):
    return RegistroDePeso.objects.create(usuario=cuenta, fecha=fecha, peso=Decimal(peso))


def test_un_registro_valido_se_guarda(david):
    registrar(david, "79.0")

    assert RegistroDePeso.objects.get(usuario=david, fecha=HOY).peso == Decimal("79.0")


def test_rn_003_06_un_solo_registro_por_dia(david):
    registrar(david, "79.0")

    with pytest.raises(IntegrityError), transaction.atomic():
        registrar(david, "78.5")


def test_dos_cuentas_pueden_pesarse_el_mismo_dia(david):
    registrar(david, "79.0")
    registrar(crear_cuenta("andrea"), "60.0")

    assert RegistroDePeso.objects.filter(fecha=HOY).count() == 2


@pytest.mark.parametrize("peso", ["19.9", "300.1"])
def test_rn_003_03_peso_fuera_de_rango(david, peso):
    with pytest.raises(IntegrityError), transaction.atomic():
        registrar(david, peso)


@pytest.mark.parametrize(("campo", "valor"), [("estatura_cm", 99), ("estatura_cm", 251), ("peso_objetivo", Decimal("19.9")), ("peso_objetivo", Decimal("300.1"))])
def test_la_cuenta_rechaza_estatura_u_objetivo_fuera_de_rango(david, campo, valor):
    setattr(david, campo, valor)
    with pytest.raises(IntegrityError), transaction.atomic():
        david.save(update_fields=[campo])


def test_una_cuenta_nueva_no_tiene_estatura_ni_objetivo(david):
    assert (david.estatura_cm, david.peso_objetivo) == (None, None)


def test_al_eliminar_la_cuenta_se_van_sus_registros(david):
    registrar(david, "79.0")
    david.delete()

    assert RegistroDePeso.objects.count() == 0
