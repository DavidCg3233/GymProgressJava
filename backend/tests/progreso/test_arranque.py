"""Arranque con las últimas sesiones y las rutinas hechas hoy (T-004-10).

Spec 004 · RF-004-07, 10 · RNF-004-01 · plan 004, sección 4.5.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from rutinas.models import Ejercicio

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db

BOGOTA = ZoneInfo("America/Bogota")


def hora(dia, h=18):
    return datetime(2026, 11, dia, h, tzinfo=BOGOTA)


@pytest.fixture
def martes_10(reloj, api):
    from .conftest import BACKEND

    reloj._ahora = hora(10, 20)
    api.client.force_login(api.cuenta, backend=BACKEND)
    return reloj


def rutina(api, nombre):
    press = Ejercicio.objects.get(usuario=api.cuenta, clave="press inclinado")
    id = nuevo_id()
    respuesta = api.put(
        f"/api/rutinas/{id}/",
        nombre=nombre,
        dias=[2],
        ejercicios=[{"ejercicio": str(press.pk), "series": 3, "reps": 10, "peso": 30}],
    )
    assert respuesta.status_code == 200
    return id


def sesion_de_rutina(api, id_rutina, inicio, nombre):
    sesion = nuevo_id()
    api.put(f"/api/sesiones/{sesion}/", nombre=nombre, inicio=inicio.isoformat(), fin=None, nota="", rutina=id_rutina)
    api.serie(api.ejercicio(sesion, momento=inicio), momento=inicio)
    fin = inicio.replace(hour=inicio.hour + 1)
    api.put(f"/api/sesiones/{sesion}/", nombre=nombre, inicio=inicio.isoformat(), fin=fin.isoformat(), nota="", rutina=id_rutina)
    return sesion


def arranque(api):
    respuesta = api.get("/api/arranque/")
    assert respuesta.status_code == 200
    return respuesta.json()


def test_rf_004_07_las_3_sesiones_terminadas_mas_recientes(api, martes_10):
    pecho = rutina(api, "Pecho")
    api.sesion_terminada([(30, 10)], inicio=hora(5), nombre="Uno")
    api.sesion_terminada([(30, 10)], inicio=hora(6), nombre="Dos")
    tres = api.sesion_terminada([(30, 10)], inicio=hora(7), nombre="Tres")
    cuatro = sesion_de_rutina(api, pecho, hora(9), "Pecho")

    recientes = arranque(api)["recientes"]

    assert [s["nombre"] for s in recientes] == ["Pecho", "Tres", "Dos"]
    assert recientes[0] == {"id": cuatro, "nombre": "Pecho", "inicio": hora(9).isoformat(), "rutina": pecho}
    assert recientes[1]["id"] == tres
    assert recientes[1]["rutina"] is None


def test_ni_la_sesion_en_curso_ni_una_sin_series_son_recientes(api, martes_10):
    api.sesion_terminada([(30, 10)], inicio=hora(5), nombre="Con series")
    vacia = api.sesion(inicio=hora(6), nombre="Vacía")
    api.terminar(vacia, hora(6), nombre="Vacía")
    api.sesion(inicio=hora(10, 19), nombre="En curso")

    assert [s["nombre"] for s in arranque(api)["recientes"]] == ["Con series"]


def test_rf_004_10_rutinas_hechas_hoy_en_hora_de_colombia(api, martes_10):
    pecho = rutina(api, "Pecho")
    pierna = rutina(api, "Pierna")
    espalda = rutina(api, "Espalda")
    sesion_de_rutina(api, pecho, hora(10, 7), "Pecho")  # hoy
    sesion_de_rutina(api, pierna, hora(9, 22), "Pierna")  # ayer a las 10 p. m.
    api.put(f"/api/sesiones/{nuevo_id()}/", nombre="Espalda", inicio=hora(10, 19).isoformat(), fin=None, nota="", rutina=espalda)

    assert arranque(api)["hechas_hoy"] == {"fecha": "2026-11-10", "rutinas": [pecho]}


def test_sin_sesiones_no_hay_recientes_ni_hechas(api, martes_10):
    datos = arranque(api)

    assert datos["recientes"] == []
    assert datos["hechas_hoy"] == {"fecha": "2026-11-10", "rutinas": []}


def test_las_recientes_de_otra_cuenta_no_aparecen(api, otra, martes_10):
    otra.sesion_terminada([(30, 10)], inicio=hora(9), nombre="Ajena")

    assert arranque(api)["recientes"] == []
