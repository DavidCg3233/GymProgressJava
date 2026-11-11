"""Sesiones enlazadas con rutinas y catálogo, y arranque ampliado (T-002-10, T-002-11).

Spec 006 · RF-006-01, 17 · Spec 002 · RF-002-09, 13 · CA-002-13a ·
plan 002, secciones 4.3 a 4.5.
"""

import pytest

from rutinas.models import Ejercicio, GrupoMuscular
from sesiones.models import Sesion, SesionEjercicio

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db

ARRANQUE = "/api/arranque/"


def ej(api, clave):
    return str(Ejercicio.objects.get(usuario=api.cuenta, clave=clave).pk)


def crear_rutina(api, nombre="Pecho", series=3):
    id = nuevo_id()
    api.put(
        f"/api/rutinas/{id}/",
        nombre=nombre,
        dias=[1],
        ejercicios=[{"ejercicio": ej(api, "press inclinado"), "series": series, "reps": 10, "peso": 30}],
    )
    return id


def empezar(api, ahora, rutina=None, id=None):
    id = id or nuevo_id()
    respuesta = api.put(f"/api/sesiones/{id}/", nombre="", inicio=ahora.isoformat(), fin=None, nota="", rutina=rutina)
    return id, respuesta


# --- RF-006-01: la sesión recuerda de qué rutina salió ----------------------


def test_una_sesion_empezada_desde_una_rutina_queda_enlazada(api, ahora):
    rutina = crear_rutina(api)

    id, respuesta = empezar(api, ahora, rutina=rutina)

    assert respuesta.status_code == 200
    assert respuesta.json()["sesion"]["rutina"] == rutina
    assert str(Sesion.objects.get(pk=id).rutina_id) == rutina


def test_una_sesion_libre_no_tiene_rutina(api, ahora):
    _, respuesta = empezar(api, ahora)

    assert respuesta.json()["sesion"]["rutina"] is None


@pytest.mark.parametrize("rutina", ["no-es-un-uuid", 5, "00000000-0000-0000-0000-000000000000"])
def test_una_rutina_inexistente_se_ignora_y_la_sesion_se_guarda_igual(api, ahora, rutina):
    # Pudo eliminarse mientras el celular estaba sin señal: rechazar la sesión perdería el entrenamiento.
    _, respuesta = empezar(api, ahora, rutina=rutina)

    assert respuesta.status_code == 200
    assert respuesta.json()["sesion"]["rutina"] is None


def test_la_rutina_de_otra_persona_se_ignora(api, otra, ahora):
    ajena = crear_rutina(otra)

    id, respuesta = empezar(api, ahora, rutina=ajena)

    assert respuesta.status_code == 200
    assert Sesion.objects.get(pk=id).rutina_id is None


def test_terminar_la_sesion_no_le_quita_la_rutina(api, ahora):
    rutina = crear_rutina(api)
    id, _ = empezar(api, ahora, rutina=rutina)
    api.serie(api.ejercicio(id))

    api.terminar(id, ahora)  # el cierre no vuelve a enviar la rutina

    assert str(Sesion.objects.get(pk=id).rutina_id) == rutina


def test_ca_002_13a_modificar_la_rutina_no_altera_la_sesion_en_curso(api, ahora):
    rutina = crear_rutina(api, series=3)
    id, _ = empezar(api, ahora, rutina=rutina)
    ejercicio = api.ejercicio(id, nombre="Press inclinado")
    for numero in (1, 2, 3):
        api.serie(ejercicio, numero=numero, confirmada=False)

    api.put(
        f"/api/rutinas/{rutina}/",
        nombre="Pecho",
        dias=[1],
        ejercicios=[{"ejercicio": ej(api, "press inclinado"), "series": 4, "reps": 10, "peso": 30}],
    )

    sesion = api.get(f"/api/sesiones/{id}/").json()["sesion"]
    assert len(sesion["ejercicios"][0]["series"]) == 3


# --- Plan 002, 4.3: el servidor enlaza cada ejercicio con el catálogo -------


def test_un_ejercicio_de_sesion_queda_enlazado_al_del_catalogo(api, ahora):
    id, _ = empezar(api, ahora)

    hecho = api.ejercicio(id, nombre="press INCLINADO", grupo="Pecho")

    assert SesionEjercicio.objects.get(pk=hecho).ejercicio == Ejercicio.objects.get(usuario=api.cuenta, clave="press inclinado")


def test_rf_002_09_un_ejercicio_nuevo_de_una_sesion_entra_al_catalogo_con_su_grupo(api, ahora):
    id, _ = empezar(api, ahora)

    hecho = api.ejercicio(id, nombre="Burpees", grupo="Cardio")

    burpees = Ejercicio.objects.get(usuario=api.cuenta, clave="burpees")
    assert burpees.grupo.nombre == "Cardio"
    assert SesionEjercicio.objects.get(pk=hecho).ejercicio == burpees
    assert GrupoMuscular.objects.filter(usuario=api.cuenta).count() == 9


def test_el_ejercicio_nuevo_entra_solo_al_catalogo_de_quien_entrena(api, otra, ahora):
    id, _ = empezar(api, ahora)

    api.ejercicio(id, nombre="Burpees", grupo="Cardio")

    assert not Ejercicio.objects.filter(usuario=otra.cuenta, clave="burpees").exists()


# --- RF-006-17: el arranque trae lo necesario para trabajar sin señal -------


def test_el_arranque_trae_el_catalogo_y_las_rutinas(api):
    rutina = crear_rutina(api)

    datos = api.get(ARRANQUE).json()

    assert len(datos["catalogo"]["grupos"]) == 8
    assert len(datos["catalogo"]["ejercicios"]) == 40
    assert [r["id"] for r in datos["rutinas"]] == [rutina]
    assert datos["rutinas"][0]["ejercicios"][0]["nombre"] == "Press inclinado"


def test_el_arranque_no_trae_nada_de_otra_persona(api, otra):
    crear_rutina(otra, nombre="De Andrea")

    datos = api.get(ARRANQUE).json()

    assert datos["rutinas"] == []
    ajenos = {str(e.pk) for e in Ejercicio.objects.filter(usuario=otra.cuenta)}
    assert not ajenos & {e["id"] for e in datos["catalogo"]["ejercicios"]}
