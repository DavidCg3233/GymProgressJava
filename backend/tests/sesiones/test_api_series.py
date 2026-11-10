"""Ejercicios y series dentro de una sesión (T-006-19).

Spec 006 · RF-006-03, 12, 13, 14, 23, 24.
"""

from datetime import timedelta

import pytest

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db


def detalle(api, sesion):
    return api.get(f"/api/sesiones/{sesion}/").json()["sesion"]


# --- RF-006-13: agregar un ejercicio ----------------------------------------


def test_ca_006_13a_se_agrega_un_ejercicio_a_la_sesion(api, ahora):
    sesion = api.sesion(inicio=ahora)

    api.ejercicio(sesion, nombre="Aperturas con mancuerna", grupo="Pecho", orden=1)

    ejercicios = detalle(api, sesion)["ejercicios"]
    assert [(e["nombre"], e["grupo"], e["orden"]) for e in ejercicios] == [("Aperturas con mancuerna", "Pecho", 1)]


def test_los_ejercicios_salen_en_su_orden(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.ejercicio(sesion, nombre="Fondos", orden=2)
    api.ejercicio(sesion, nombre="Press inclinado", orden=1)

    assert [e["nombre"] for e in detalle(api, sesion)["ejercicios"]] == ["Press inclinado", "Fondos"]


@pytest.mark.parametrize(
    ("cambios", "campo", "mensaje"),
    [
        ({"nombre": "  "}, "nombre", "Escribe el nombre del ejercicio."),
        ({"nombre": "e" * 51}, "nombre", "El nombre del ejercicio admite máximo 50 caracteres."),
        ({"grupo": ""}, "grupo", "Elige el grupo muscular."),
        ({"nota": "a" * 281}, "nota", "La nota admite máximo 280 caracteres."),
        ({"orden": 0}, "orden", "El orden del ejercicio no es válido."),
        ({"orden": "primero"}, "orden", "El orden del ejercicio no es válido."),
    ],
)
def test_un_ejercicio_invalido_se_rechaza_indicando_el_campo(api, ahora, cambios, campo, mensaje):
    sesion = api.sesion(inicio=ahora)
    datos = {"nombre": "Press inclinado", "grupo": "Pecho", "orden": 1, "nota": ""} | cambios

    respuesta = api.put(f"/api/sesiones/{sesion}/ejercicios/{nuevo_id()}/", **datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": campo}


def test_ca_006_23_la_nota_de_un_ejercicio_se_guarda(api, ahora):
    sesion = api.sesion(inicio=ahora)

    api.ejercicio(sesion, nota="subir a 35")

    assert detalle(api, sesion)["ejercicios"][0]["nota"] == "subir a 35"


# --- RF-006-03: confirmar una serie -----------------------------------------


def test_ca_006_03a_confirmar_una_serie_la_guarda_de_inmediato(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)

    id = api.serie(ejercicio, numero=1, peso=30, reps=10, confirmada=True)

    assert detalle(api, sesion)["ejercicios"][0]["series"] == [
        {"id": id, "numero": 1, "peso": 30.0, "reps": 10, "confirmada": True}
    ]


def test_reenviar_la_misma_serie_no_la_duplica(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    id = api.serie(ejercicio, numero=1, peso=30, reps=10)

    api.serie(ejercicio, numero=1, peso=30, reps=10, id=id)

    assert len(detalle(api, sesion)["ejercicios"][0]["series"]) == 1


def test_las_series_salen_en_orden_de_numero(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    api.serie(ejercicio, numero=2, peso=32.5, reps=8)
    api.serie(ejercicio, numero=1, peso=30, reps=10)

    assert [s["numero"] for s in detalle(api, sesion)["ejercicios"][0]["series"]] == [1, 2]


# --- RF-006-24: bordes de CA-006-24a, ahora en el servidor ------------------


@pytest.mark.parametrize(
    ("peso", "reps", "campo", "mensaje"),
    [
        (-0.5, 8, "peso", "El peso debe estar entre 0 y 500 kg."),
        (500.5, 1, "peso", "El peso debe estar entre 0 y 500 kg."),
        (30.3, 10, "peso", "El peso va de a 0,5 kg."),
        (None, 10, "peso", "Escribe el peso."),
        (30, 0, "reps", "Las repeticiones deben estar entre 1 y 100."),
        (30, 101, "reps", "Las repeticiones deben estar entre 1 y 100."),
        (30, 8.5, "reps", "Las repeticiones deben ser un número entero."),
    ],
)
def test_ca_006_24a_una_serie_fuera_de_rango_se_rechaza_en_el_servidor(api, ahora, peso, reps, campo, mensaje):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)

    respuesta = api.put(f"/api/series/{nuevo_id()}/", ejercicio=ejercicio, numero=1, peso=peso, reps=reps, confirmada=True)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": campo}
    assert detalle(api, sesion)["ejercicios"][0]["series"] == []


@pytest.mark.parametrize(("peso", "reps"), [(0, 8), (500, 1), (30, 100)])
def test_ca_006_24a_los_valores_en_el_limite_se_aceptan(api, ahora, peso, reps):
    sesion = api.sesion(inicio=ahora)

    api.serie(api.ejercicio(sesion), peso=peso, reps=reps)


def test_una_serie_necesita_un_ejercicio_que_exista(api, ahora):
    respuesta = api.put(f"/api/series/{nuevo_id()}/", ejercicio=nuevo_id(), numero=1, peso=30, reps=10, confirmada=True)

    assert respuesta.status_code == 404


def test_confirmada_debe_ser_verdadero_o_falso(api, ahora):
    sesion = api.sesion(inicio=ahora)

    respuesta = api.put(
        f"/api/series/{nuevo_id()}/", ejercicio=api.ejercicio(sesion), numero=1, peso=30, reps=10, confirmada="sí"
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == "confirmada"


# --- RF-006-12: agregar y quitar series -------------------------------------


def test_ca_006_12a_se_puede_agregar_una_cuarta_serie(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    for numero in (1, 2, 3):
        api.serie(ejercicio, numero=numero)

    api.serie(ejercicio, numero=4, peso=32.5, reps=6, confirmada=False)

    assert len(detalle(api, sesion)["ejercicios"][0]["series"]) == 4


def test_un_ejercicio_admite_maximo_10_series(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)

    respuesta = api.put(f"/api/series/{nuevo_id()}/", ejercicio=ejercicio, numero=11, peso=30, reps=10, confirmada=True)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "Un ejercicio admite entre 1 y 10 series.", "campo": "numero"}


def test_dos_series_distintas_no_pueden_tener_el_mismo_numero(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    api.serie(ejercicio, numero=1)

    respuesta = api.put(f"/api/series/{nuevo_id()}/", ejercicio=ejercicio, numero=1, peso=30, reps=10, confirmada=True)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "Ese ejercicio ya tiene una serie con ese número.", "campo": "numero"}


def test_se_puede_quitar_una_serie(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    api.serie(ejercicio, numero=1)
    sobrante = api.serie(ejercicio, numero=2)

    respuesta = api.delete(f"/api/series/{sobrante}/")

    assert respuesta.status_code == 204
    assert [s["numero"] for s in detalle(api, sesion)["ejercicios"][0]["series"]] == [1]


def test_quitar_una_serie_que_ya_no_existe_responde_que_no_esta(api, ahora):
    # Igual que con una serie ajena: no se distingue "no existe" de "no es tuya".
    # La cola de pendientes del celular trata este 404 como "ya estaba quitada".
    sesion = api.sesion(inicio=ahora)
    serie = api.serie(api.ejercicio(sesion))
    api.delete(f"/api/series/{serie}/")

    assert api.delete(f"/api/series/{serie}/").status_code == 404


# --- RF-006-14: corregir solo mientras esté en curso ------------------------


def test_ca_006_14a_en_curso_se_puede_corregir_una_serie_confirmada(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    serie = api.serie(ejercicio, numero=1, peso=30, reps=10)

    api.serie(ejercicio, numero=1, peso=32.5, reps=10, id=serie)

    assert detalle(api, sesion)["ejercicios"][0]["series"][0]["peso"] == 32.5


@pytest.fixture
def terminada(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    serie = api.serie(ejercicio, numero=1, peso=30, reps=10)
    api.terminar(sesion, ahora)
    return sesion, ejercicio, serie


MENSAJE_TERMINADA = "Esta sesión ya terminó y no se puede modificar."


def test_ca_006_14b_terminada_no_se_puede_corregir_una_serie_con_otros_valores(api, terminada, ahora):
    _, ejercicio, serie = terminada

    respuesta = api.put(
        f"/api/series/{serie}/",
        ejercicio=ejercicio,
        numero=1,
        peso=40,
        reps=10,
        confirmada=True,
        momento=(ahora + timedelta(hours=1, minutes=5)).isoformat(),  # después de terminarla
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {"mensaje": MENSAJE_TERMINADA}


def test_terminada_no_se_pueden_agregar_series_ni_ejercicios_ni_quitar_series(api, terminada, ahora):
    sesion, ejercicio, serie = terminada
    despues = (ahora + timedelta(hours=1, minutes=5)).isoformat()

    assert api.put(f"/api/series/{nuevo_id()}/", ejercicio=ejercicio, numero=2, peso=30, reps=10, confirmada=True, momento=despues).status_code == 409
    assert api.put(f"/api/sesiones/{sesion}/ejercicios/{nuevo_id()}/", nombre="Fondos", grupo="Pecho", orden=2, nota="", momento=despues).status_code == 409
    assert api.delete(f"/api/series/{serie}/", momento=despues).status_code == 409


def test_el_cierre_automatico_tambien_congela_las_series(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    api.serie(ejercicio, numero=1)

    reloj.avanzar(hours=2, minutes=1)

    respuesta = api.put(f"/api/series/{nuevo_id()}/", ejercicio=ejercicio, numero=2, peso=30, reps=10, confirmada=True)
    assert respuesta.status_code == 409
