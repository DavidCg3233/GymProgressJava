"""API del catálogo (T-002-06, T-002-07).

Spec 002 · RF-002-08, 09, 15, 16, 17, 18, 19 · CA-002-09a, 16a, 18a, 19a ·
plan 002, sección 4.4.
"""

from datetime import timedelta

import pytest

from rutinas.models import Ejercicio, GrupoMuscular, Rutina

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db

CATALOGO = "/api/catalogo/"


def grupo(api, clave):
    return str(GrupoMuscular.objects.get(usuario=api.cuenta, clave=clave).pk)


def ejercicio(api, clave):
    return str(Ejercicio.objects.get(usuario=api.cuenta, clave=clave).pk)


def rutina_con(api, *claves, nombre="Pecho"):
    id = nuevo_id()
    respuesta = api.put(
        f"/api/rutinas/{id}/",
        nombre=nombre,
        dias=[],
        ejercicios=[{"ejercicio": ejercicio(api, c), "series": 3, "reps": 10, "peso": 30} for c in claves],
    )
    assert respuesta.status_code == 200, respuesta.content
    return id


# --- Listar -----------------------------------------------------------------


def test_el_catalogo_trae_los_grupos_y_ejercicios_de_la_persona(api):
    datos = api.get(CATALOGO).json()

    assert len(datos["grupos"]) == 8
    assert len(datos["ejercicios"]) == 40
    press = next(e for e in datos["ejercicios"] if e["nombre"] == "Press inclinado")
    pecho = next(g for g in datos["grupos"] if g["nombre"] == "Pecho")
    assert press == {"id": press["id"], "nombre": "Press inclinado", "grupo": pecho["id"]}


# --- Grupos (RF-002-19) -----------------------------------------------------


def test_crear_un_grupo(api):
    id = nuevo_id()

    respuesta = api.put(f"/api/catalogo/grupos/{id}/", nombre="Cardio")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"grupo": {"id": id, "nombre": "Cardio"}}


def test_renombrar_un_grupo(api):
    id = grupo(api, "pierna")

    api.put(f"/api/catalogo/grupos/{id}/", nombre="Piernas")

    assert GrupoMuscular.objects.get(pk=id).nombre == "Piernas"


@pytest.mark.parametrize(
    ("nombre", "mensaje"),
    [
        ("  ", "Elige el grupo muscular."),
        ("g" * 31, "El grupo muscular admite máximo 30 caracteres."),
        ("PECHO", "Ya tienes un grupo con ese nombre."),
    ],
)
def test_un_grupo_invalido_o_repetido_se_rechaza(api, nombre, mensaje):
    respuesta = api.put(f"/api/catalogo/grupos/{nuevo_id()}/", nombre=nombre)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": "nombre"}


def test_ca_002_19a_un_grupo_con_ejercicios_no_se_elimina(api):
    respuesta = api.delete(f"/api/catalogo/grupos/{grupo(api, 'pecho')}/")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"mensaje": "Mueve o elimina primero los ejercicios de este grupo."}


def test_un_grupo_vacio_si_se_elimina(api):
    id = nuevo_id()
    api.put(f"/api/catalogo/grupos/{id}/", nombre="Cardio")

    assert api.delete(f"/api/catalogo/grupos/{id}/").status_code == 204
    assert not GrupoMuscular.objects.filter(pk=id).exists()


# --- Ejercicios (RF-002-09, 15) ---------------------------------------------


def test_ca_002_09a_crear_un_ejercicio_en_un_grupo(api):
    id = nuevo_id()

    respuesta = api.put(f"/api/catalogo/ejercicios/{id}/", nombre="Press en máquina", grupo=grupo(api, "pecho"))

    assert respuesta.status_code == 200
    assert respuesta.json() == {"ejercicio": {"id": id, "nombre": "Press en máquina", "grupo": grupo(api, "pecho")}}


def test_renombrar_y_cambiar_de_grupo_un_ejercicio_predefinido(api):
    id = ejercicio(api, "fondos")

    api.put(f"/api/catalogo/ejercicios/{id}/", nombre="Fondos en paralelas", grupo=grupo(api, "triceps"))

    fondos = Ejercicio.objects.get(pk=id)
    assert (fondos.nombre, fondos.grupo.nombre) == ("Fondos en paralelas", "Tríceps")


def test_ca_002_rn_un_ejercicio_que_ya_tengo_se_rechaza_aunque_cambien_mayusculas(api):
    respuesta = api.put(f"/api/catalogo/ejercicios/{nuevo_id()}/", nombre="press de BANCA", grupo=grupo(api, "pecho"))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "Ya tienes un ejercicio con ese nombre.", "campo": "nombre"}


def test_renombrar_un_ejercicio_con_su_mismo_nombre_no_choca_consigo_mismo(api):
    id = ejercicio(api, "fondos")

    assert api.put(f"/api/catalogo/ejercicios/{id}/", nombre="FONDOS", grupo=grupo(api, "pecho")).status_code == 200


@pytest.mark.parametrize("grupo_dado", ["no-es-un-uuid", None])
def test_un_ejercicio_sin_un_grupo_valido_se_rechaza(api, grupo_dado):
    respuesta = api.put(f"/api/catalogo/ejercicios/{nuevo_id()}/", nombre="Burpees", grupo=grupo_dado)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "Elige el grupo muscular.", "campo": "grupo"}


def test_no_se_puede_usar_el_grupo_de_otra_persona(api, otra):
    respuesta = api.put(f"/api/catalogo/ejercicios/{nuevo_id()}/", nombre="Burpees", grupo=grupo(otra, "pecho"))

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == "grupo"


# --- Eliminar un ejercicio (RF-002-16, 17, 18) ------------------------------


def test_ca_002_16a_antes_de_eliminar_se_ve_en_que_rutinas_esta(api):
    pecho = rutina_con(api, "press inclinado", "fondos", nombre="Pecho")
    solo = rutina_con(api, "fondos", nombre="Solo fondos")

    uso = api.get(f"/api/catalogo/ejercicios/{ejercicio(api, 'fondos')}/uso/").json()

    assert uso == {
        "rutinas": [
            {"id": pecho, "nombre": "Pecho", "quedaria_vacia": False},
            {"id": solo, "nombre": "Solo fondos", "quedaria_vacia": True},
        ]
    }


def test_ca_002_16a_eliminarlo_lo_quita_del_catalogo_y_de_las_rutinas_pero_no_de_las_sesiones(api, ahora):
    pecho = rutina_con(api, "press inclinado", "fondos")
    sesion = api.sesion_terminada([(0, 12)], inicio=ahora - timedelta(days=1), ejercicio="Fondos")
    id = ejercicio(api, "fondos")

    respuesta = api.delete(f"/api/catalogo/ejercicios/{id}/")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"rutinas_eliminadas": []}
    assert not Ejercicio.objects.filter(pk=id).exists()
    nombres = [e["nombre"] for e in api.get("/api/rutinas/").json()["rutinas"][0]["ejercicios"]]
    assert nombres == ["Press inclinado"]
    detalle = api.get(f"/api/sesiones/{sesion}/").json()["sesion"]
    assert detalle["ejercicios"][0]["nombre"] == "Fondos"
    assert Rutina.objects.filter(pk=pecho).exists()


def test_ca_002_18a_si_una_rutina_queda_vacia_se_elimina_tambien(api):
    rutina_con(api, "press inclinado", "fondos", nombre="Pecho")
    solo = rutina_con(api, "fondos", nombre="Solo fondos")

    respuesta = api.delete(f"/api/catalogo/ejercicios/{ejercicio(api, 'fondos')}/")

    assert respuesta.json() == {"rutinas_eliminadas": [{"id": solo, "nombre": "Solo fondos"}]}
    assert not Rutina.objects.filter(pk=solo).exists()


# --- Lo ajeno no existe (RNF-ACC-06) ----------------------------------------


def test_otra_persona_no_ve_ni_toca_el_catalogo_ajeno(api, otra):
    ajeno_grupo = grupo(api, "pecho")
    ajeno_ejercicio = ejercicio(api, "fondos")

    assert otra.put(f"/api/catalogo/grupos/{ajeno_grupo}/", nombre="Mío").status_code == 404
    assert otra.delete(f"/api/catalogo/grupos/{ajeno_grupo}/").status_code == 404
    assert otra.put(f"/api/catalogo/ejercicios/{ajeno_ejercicio}/", nombre="Mío", grupo=grupo(otra, "pecho")).status_code == 404
    assert otra.get(f"/api/catalogo/ejercicios/{ajeno_ejercicio}/uso/").status_code == 404
    assert otra.delete(f"/api/catalogo/ejercicios/{ajeno_ejercicio}/").status_code == 404
    assert Ejercicio.objects.get(pk=ajeno_ejercicio).nombre == "Fondos"


def test_sin_acceso_el_catalogo_no_responde(anonimo):
    assert anonimo.get(CATALOGO).status_code == 401
