"""Catálogo predefinido y migración de las cuentas que ya existen (T-002-04, T-002-05).

Spec 002 · RF-002-09, 10, 14 · plan 002, secciones 4.2 y 4.3.
"""

import uuid
from datetime import timedelta

import pytest
from django.apps import apps
from django.utils import timezone

from rutinas import catalogo_inicial, migracion_de_datos
from rutinas.models import Ejercicio, GrupoMuscular
from sesiones.models import Sesion, SesionEjercicio

from .conftest import crear_cuenta

pytestmark = pytest.mark.django_db


def nombres_por_grupo(usuario) -> dict[str, list[str]]:
    resultado = {}
    for ejercicio in Ejercicio.objects.filter(usuario=usuario).select_related("grupo").order_by("nombre"):
        resultado.setdefault(ejercicio.grupo.nombre, []).append(ejercicio.nombre)
    return resultado


# --- T-002-04: al crear una cuenta ------------------------------------------


def test_una_cuenta_nueva_trae_8_grupos_y_40_ejercicios():
    david = crear_cuenta()

    assert GrupoMuscular.objects.filter(usuario=david).count() == 8
    assert Ejercicio.objects.filter(usuario=david).count() == 40


def test_el_catalogo_es_el_de_la_spec():
    david = crear_cuenta()

    catalogo = nombres_por_grupo(david)

    assert sorted(catalogo) == ["Abdomen", "Bíceps", "Espalda", "Hombro", "Pantorrilla", "Pecho", "Pierna", "Tríceps"]
    assert "Press inclinado" in catalogo["Pecho"]
    assert "Plancha" in catalogo["Abdomen"]
    assert len(catalogo["Pierna"]) == 7


def test_la_lista_tiene_exactamente_40_ejercicios_sin_repetir():
    nombres = [nombre for ejercicios in catalogo_inicial.CATALOGO.values() for nombre in ejercicios]

    assert len(nombres) == 40
    assert len(set(nombres)) == 40


def test_ca_002_10a_cada_cuenta_tiene_su_propio_catalogo():
    david = crear_cuenta()
    andrea = crear_cuenta("andrea")

    banca = Ejercicio.objects.get(usuario=david, clave="press de banca")
    banca.nombre = "Bench press"
    banca.save()
    Ejercicio.objects.get(usuario=david, clave="fondos").delete()

    assert Ejercicio.objects.filter(usuario=andrea, nombre="Press de banca").exists()
    assert Ejercicio.objects.filter(usuario=andrea, nombre="Fondos").exists()


def test_cargar_dos_veces_no_duplica():
    david = crear_cuenta()

    catalogo_inicial.cargar(david, GrupoMuscular, Ejercicio)

    assert Ejercicio.objects.filter(usuario=david).count() == 40


def test_no_pisa_un_ejercicio_que_la_persona_ya_tenia_con_otro_nombre_o_grupo():
    david = crear_cuenta()
    abdomen = GrupoMuscular.objects.get(usuario=david, clave="abdomen")
    fondos = Ejercicio.objects.get(usuario=david, clave="fondos")
    fondos.nombre, fondos.grupo = "FONDOS", abdomen
    fondos.save()

    catalogo_inicial.cargar(david, GrupoMuscular, Ejercicio)

    fondos.refresh_from_db()
    assert (fondos.nombre, fondos.grupo.nombre) == ("FONDOS", "Abdomen")


# --- T-002-05: cuentas que ya existían antes de esta versión ----------------


def sesion_vieja(usuario, ejercicios):
    """Una sesión registrada antes de que existiera el catálogo: sin enlaces."""
    inicio = timezone.now() - timedelta(days=3)
    sesion = Sesion.objects.create(
        id=uuid.uuid4(), usuario=usuario, nombre="Sesión libre", inicio=inicio, fin=inicio + timedelta(hours=1)
    )
    hechos = []
    for orden, (nombre, grupo) in enumerate(ejercicios, start=1):
        hechos.append(
            SesionEjercicio.objects.create(
                id=uuid.uuid4(), sesion=sesion, nombre=nombre, clave=nombre.lower(), grupo=grupo, orden=orden
            )
        )
    return hechos


def cuenta_sin_catalogo(usuario="davidc"):
    cuenta = crear_cuenta(usuario)
    Ejercicio.objects.filter(usuario=cuenta).delete()
    GrupoMuscular.objects.filter(usuario=cuenta).delete()
    return cuenta


def test_la_migracion_le_carga_el_catalogo_a_una_cuenta_que_no_lo_tenia():
    david = cuenta_sin_catalogo()

    migracion_de_datos.aplicar(apps)

    assert Ejercicio.objects.filter(usuario=david).count() == 40


def test_la_migracion_enlaza_las_sesiones_viejas_con_el_catalogo():
    david = cuenta_sin_catalogo()
    (press,) = sesion_vieja(david, [("Press inclinado", "Pecho")])

    migracion_de_datos.aplicar(apps)

    press.refresh_from_db()
    assert press.ejercicio == Ejercicio.objects.get(usuario=david, clave="press inclinado")


def test_un_ejercicio_de_sesion_que_no_esta_en_el_catalogo_se_agrega_con_su_grupo():
    david = cuenta_sin_catalogo()
    (burpees,) = sesion_vieja(david, [("Burpees", "Cardio")])

    migracion_de_datos.aplicar(apps)

    burpees.refresh_from_db()
    assert burpees.ejercicio.nombre == "Burpees"
    assert burpees.ejercicio.grupo.nombre == "Cardio"
    assert GrupoMuscular.objects.filter(usuario=david).count() == 9


def test_la_migracion_no_mezcla_cuentas():
    david = cuenta_sin_catalogo()
    andrea = cuenta_sin_catalogo("andrea")
    (de_andrea,) = sesion_vieja(andrea, [("Burpees", "Cardio")])

    migracion_de_datos.aplicar(apps)

    de_andrea.refresh_from_db()
    assert de_andrea.ejercicio.usuario == andrea
    assert not Ejercicio.objects.filter(usuario=david, clave="burpees").exists()


def test_aplicar_la_migracion_dos_veces_no_cambia_nada():
    david = cuenta_sin_catalogo()
    sesion_vieja(david, [("Burpees", "Cardio")])
    migracion_de_datos.aplicar(apps)

    migracion_de_datos.aplicar(apps)

    assert Ejercicio.objects.filter(usuario=david).count() == 41
