"""Guardar una sesión como rutina, por la API (T-008-05 a 07).

Spec 008 · RF-008-06, 07 · RN-008-05 a 07 · CA-008-06a, 06b, 07a · RNF-ACC-06 ·
plan 008, sección 4.5.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from rutinas.models import Ejercicio, Rutina

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db


def sesion_con(api, ejercicios, nombre="", terminar=True):
    """Crea una sesión con varios ejercicios: [(nombre, grupo, [(peso, reps), ...]), ...].

    Sin terminar, empieza hace 10 minutos: con más de 2 horas se cerraría sola (RN-006-11).
    """
    inicio = timezone.now() - (timedelta(hours=1, minutes=30) if terminar else timedelta(minutes=10))
    sesion = api.sesion(inicio=inicio, nombre=nombre)
    for orden, (ejercicio, grupo, series) in enumerate(ejercicios, start=1):
        id_ejercicio = api.ejercicio(sesion, nombre=ejercicio, grupo=grupo, orden=orden, momento=inicio)
        for numero, (peso, reps) in enumerate(series, start=1):
            api.serie(id_ejercicio, numero=numero, peso=peso, reps=reps, momento=inicio)
    if terminar:
        assert api.terminar(sesion, inicio, nombre=nombre).status_code == 200
    return sesion


def a_rutina(api, sesion, **datos):
    return api.client.post(f"/api/sesiones/{sesion}/a-rutina/", data=datos, content_type="application/json")


def ejercicios_de(rutina):
    return [(p.ejercicio.nombre, p.series, float(p.peso), p.reps) for p in rutina.ejercicios.select_related("ejercicio")]


CA_06A = [
    ("Sentadilla", "Pierna", [(60, 8), (70, 6), (70, 5)]),
    ("Prensa", "Pierna", [(120, 10), (120, 10)]),
]


# --- Rutina nueva (T-008-05) -------------------------------------------------


def test_ca_008_06a_una_sesion_libre_se_vuelve_rutina_nueva(api):
    sesion = sesion_con(api, CA_06A)
    id_rutina = nuevo_id()

    respuesta = a_rutina(api, sesion, modo="nueva", id_rutina=id_rutina, nombre="Pierna B", dias=[6], confirmar=True)

    assert respuesta.status_code == 200, respuesta.content
    rutina = Rutina.objects.get(pk=id_rutina)
    assert (rutina.nombre, respuesta.json()["rutina"]["dias"]) == ("Pierna B", [6])
    assert ejercicios_de(rutina) == [("Sentadilla", 3, 70.0, 6), ("Prensa", 2, 120.0, 10)]


def test_la_vista_previa_muestra_los_cambios_y_no_guarda_nada(api):
    sesion = sesion_con(api, CA_06A)

    respuesta = a_rutina(api, sesion, modo="nueva", confirmar=False)

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "rutina": None,
        "cambios": [
            {"tipo": "agrega", "nombre": "Sentadilla", "series": 3, "antes": None, "despues": {"peso": 70.0, "reps": 6}},
            {"tipo": "agrega", "nombre": "Prensa", "series": 2, "antes": None, "despues": {"peso": 120.0, "reps": 10}},
        ],
    }
    assert Rutina.objects.filter(usuario=api.cuenta).count() == 0


def test_ca_008_06b_un_nombre_repetido_se_rechaza_sin_guardar(api):
    sesion = sesion_con(api, CA_06A)
    a_rutina(api, sesion, modo="nueva", id_rutina=nuevo_id(), nombre="Pierna B", dias=[], confirmar=True)

    respuesta = a_rutina(api, sesion, modo="nueva", id_rutina=nuevo_id(), nombre="pierna b", dias=[], confirmar=True)

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == "nombre"
    assert Rutina.objects.filter(usuario=api.cuenta).count() == 1


def test_una_sesion_en_curso_no_se_puede_guardar_todavia(api):
    sesion = sesion_con(api, CA_06A, terminar=False)

    respuesta = a_rutina(api, sesion, modo="nueva", confirmar=False)

    assert respuesta.status_code == 409
    assert respuesta.json()["mensaje"] == "Termina la sesión antes de guardarla como rutina."


def test_un_ejercicio_borrado_del_catalogo_vuelve_al_catalogo(api):
    sesion = sesion_con(api, [("Bici", "Cardio", [(0, 20)])])
    bici = Ejercicio.objects.get(usuario=api.cuenta, clave="bici")
    api.delete(f"/api/catalogo/ejercicios/{bici.pk}/")
    id_rutina = nuevo_id()

    respuesta = a_rutina(api, sesion, modo="nueva", id_rutina=id_rutina, nombre="Cardio", dias=[], confirmar=True)

    assert respuesta.status_code == 200, respuesta.content
    assert ejercicios_de(Rutina.objects.get(pk=id_rutina)) == [("Bici", 1, 0.0, 20)]


@pytest.mark.parametrize("modo", ["", "borrar", None])
def test_un_modo_desconocido_se_rechaza(api, modo):
    sesion = sesion_con(api, CA_06A)

    assert a_rutina(api, sesion, modo=modo, confirmar=False).status_code == 400


def test_confirmar_debe_ser_si_o_no(api):
    sesion = sesion_con(api, CA_06A)

    assert a_rutina(api, sesion, modo="nueva", confirmar="si").status_code == 400


# --- Actualizar una rutina (T-008-06) ----------------------------------------


def rutina_pierna(api):
    def ej(clave):
        return str(Ejercicio.objects.get(usuario=api.cuenta, clave=clave).pk)

    id_rutina = nuevo_id()
    respuesta = api.put(
        f"/api/rutinas/{id_rutina}/",
        nombre="Pierna",
        dias=[1],
        ejercicios=[
            {"ejercicio": ej("sentadilla"), "series": 3, "reps": 6, "peso": 65},
            {"ejercicio": ej("curl femoral"), "series": 3, "reps": 12, "peso": 30},
        ],
    )
    assert respuesta.status_code == 200, respuesta.content
    return id_rutina


def test_ca_008_07a_actualizar_suma_mejora_y_no_quita(api):
    id_rutina = rutina_pierna(api)
    sesion = sesion_con(api, [("Sentadilla", "Pierna", [(70, 6), (65, 6)]), ("Prensa", "Pierna", [(120, 10), (110, 10)])])

    vista = a_rutina(api, sesion, modo="actualizar", rutina=id_rutina, confirmar=False).json()

    assert [(c["tipo"], c["nombre"]) for c in vista["cambios"]] == [
        ("mejora", "Sentadilla"),
        ("igual", "Curl femoral"),
        ("agrega", "Prensa"),
    ]
    assert vista["cambios"][0]["antes"] == {"peso": 65.0, "reps": 6}
    assert ejercicios_de(Rutina.objects.get(pk=id_rutina)) == [("Sentadilla", 3, 65.0, 6), ("Curl femoral", 3, 30.0, 12)]

    respuesta = a_rutina(api, sesion, modo="actualizar", rutina=id_rutina, confirmar=True)

    assert respuesta.status_code == 200, respuesta.content
    rutina = Rutina.objects.get(pk=id_rutina)
    assert (rutina.nombre, rutina.dias) == ("Pierna", 1)  # nombre y días no cambian
    assert ejercicios_de(rutina) == [
        ("Sentadilla", 3, 70.0, 6),
        ("Curl femoral", 3, 30.0, 12),
        ("Prensa", 2, 120.0, 10),
    ]


def test_actualizar_que_pase_de_20_no_cambia_nada(api):
    nombres = [e.nombre for e in Ejercicio.objects.filter(usuario=api.cuenta).order_by("nombre")][:19]
    id_rutina = nuevo_id()
    api.put(
        f"/api/rutinas/{id_rutina}/",
        nombre="Larga",
        dias=[],
        ejercicios=[
            {"ejercicio": str(Ejercicio.objects.get(usuario=api.cuenta, nombre=n).pk), "series": 1, "reps": 10, "peso": 10}
            for n in nombres
        ],
    )
    sesion = sesion_con(api, [("Nuevo A", "Pecho", [(10, 10)]), ("Nuevo B", "Pecho", [(10, 10)])])

    respuesta = a_rutina(api, sesion, modo="actualizar", rutina=id_rutina, confirmar=True)

    assert respuesta.status_code == 400
    assert "sobra 1" in respuesta.json()["mensaje"]
    assert Rutina.objects.get(pk=id_rutina).ejercicios.count() == 19


# --- Permisos (T-008-07) -----------------------------------------------------


def test_la_sesion_de_otra_cuenta_no_existe(api, otra):
    ajena = sesion_con(otra, CA_06A)

    assert a_rutina(api, ajena, modo="nueva", confirmar=False).status_code == 404


def test_la_rutina_de_otra_cuenta_no_se_puede_actualizar(api, otra):
    ajena = rutina_pierna(otra)
    mia = sesion_con(api, CA_06A)

    assert a_rutina(api, mia, modo="actualizar", rutina=ajena, confirmar=True).status_code == 404
    assert Rutina.objects.get(pk=ajena).ejercicios.count() == 2


def test_sin_acceso_no_se_puede(anonimo, api):
    sesion = sesion_con(api, CA_06A)

    assert a_rutina(anonimo, sesion, modo="nueva", confirmar=False).status_code == 401
