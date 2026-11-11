"""Historial, eliminar y datos de arranque (T-006-21, T-006-22).

Spec 006 · RF-006-04, 09, 10, 11, 15, 17, 23 · RN-006-08, 09, 16.
"""

from datetime import timedelta

import pytest

pytestmark = pytest.mark.django_db

LISTA = "/api/sesiones/"
ARRANQUE = "/api/arranque/"


# --- RF-006-09 y 10: historial ----------------------------------------------


def test_el_historial_lista_las_terminadas_de_la_mas_reciente_a_la_mas_antigua(api, ahora):
    vieja = api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=7), nombre="Vieja")
    nueva = api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=1), nombre="Nueva")

    sesiones = api.get(LISTA).json()["sesiones"]

    assert [s["id"] for s in sesiones] == [nueva, vieja]
    assert sesiones[0] == {
        "id": nueva,
        "nombre": "Nueva",
        "inicio": (ahora - timedelta(days=1)).isoformat(),
        "fin": (ahora - timedelta(days=1) + timedelta(hours=1)).isoformat(),
        "ejercicios": 1,
        "series": 1,
    }


def test_la_sesion_en_curso_no_aparece_en_el_historial(api, ahora):
    api.sesion(inicio=ahora)

    assert api.get(LISTA).json()["sesiones"] == []


def test_ca_006_10a_al_abrir_una_sesion_se_ven_sus_ejercicios_y_series(api, ahora):
    inicio = ahora - timedelta(days=7)
    sesion = api.sesion_terminada([(30, 10), (32.5, 8), (32.5, 7)], inicio=inicio, nombre="Pecho")

    detalle = api.get(f"{LISTA}{sesion}/").json()["sesion"]

    assert detalle["nombre"] == "Pecho"
    assert [(s["peso"], s["reps"]) for s in detalle["ejercicios"][0]["series"]] == [(30.0, 10), (32.5, 8), (32.5, 7)]


def test_el_historial_se_entrega_por_paginas_de_20(api, ahora):
    for dias in range(1, 23):
        api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=dias))

    primera = api.get(LISTA).json()
    segunda = api.get(f"{LISTA}?pagina=2").json()

    assert (len(primera["sesiones"]), primera["hay_mas"]) == (20, True)
    assert (len(segunda["sesiones"]), segunda["hay_mas"]) == (2, False)


@pytest.mark.parametrize("pagina", ["0", "-1", "abc", "999"])
def test_una_pagina_que_no_existe_no_rompe_el_servidor(api, ahora, pagina):
    api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=1))

    assert api.get(f"{LISTA}?pagina={pagina}").status_code == 200


# --- RF-006-15: eliminar ----------------------------------------------------


def test_ca_006_15a_eliminar_una_sesion_la_saca_del_historial(api, ahora):
    sesiones = [api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=d)) for d in (1, 2, 3)]

    respuesta = api.delete(f"{LISTA}{sesiones[0]}/")

    assert respuesta.status_code == 204
    assert len(api.get(LISTA).json()["sesiones"]) == 2
    assert api.get(f"{LISTA}{sesiones[0]}/").status_code == 404


def test_ca_006_15a_las_series_eliminadas_dejan_de_contar_como_ultima_vez(api, ahora):
    api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=7))
    reciente = api.sesion_terminada([(40, 5)], inicio=ahora - timedelta(days=1))

    api.delete(f"{LISTA}{reciente}/")

    assert api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]["series"] == [{"numero": 1, "peso": 30.0, "reps": 10}]


def test_una_sesion_en_curso_no_se_elimina_desde_el_historial(api, ahora):
    sesion = api.sesion(inicio=ahora)

    respuesta = api.delete(f"{LISTA}{sesion}/")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"mensaje": "Termina la sesión antes de eliminarla."}


# --- RF-006-17: arranque ----------------------------------------------------


def test_sin_datos_el_arranque_viene_vacio(api):
    datos = api.get(ARRANQUE).json()

    assert (datos["sesion_en_curso"], datos["ultima_vez"], datos["rutinas"]) == (None, {}, [])


def test_el_arranque_trae_la_sesion_en_curso_completa(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion), peso=30, reps=10)

    en_curso = api.get(ARRANQUE).json()["sesion_en_curso"]

    assert en_curso["id"] == sesion
    assert en_curso["ejercicios"][0]["series"][0]["peso"] == 30.0


# --- RF-006-04 y RN-006-08: la última vez -----------------------------------


def test_ca_006_04a_el_arranque_trae_lo_registrado_la_ultima_vez_en_cada_serie(api, ahora):
    api.sesion_terminada([(30, 10), (32.5, 8), (32.5, 6)], inicio=ahora - timedelta(days=7))

    ultima = api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]

    assert ultima["nombre"] == "Press inclinado"
    assert ultima["grupo"] == "Pecho"
    assert ultima["series"] == [
        {"numero": 1, "peso": 30.0, "reps": 10},
        {"numero": 2, "peso": 32.5, "reps": 8},
        {"numero": 3, "peso": 32.5, "reps": 6},
    ]


def test_rn_006_08_si_la_sesion_mas_reciente_no_tiene_una_serie_se_toma_de_la_anterior(api, ahora):
    api.sesion_terminada([(30, 10), (32.5, 8), (32.5, 6)], inicio=ahora - timedelta(days=7))
    api.sesion_terminada([(35, 5), (35, 4)], inicio=ahora - timedelta(days=1))

    series = api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]["series"]

    assert series == [
        {"numero": 1, "peso": 35.0, "reps": 5},
        {"numero": 2, "peso": 35.0, "reps": 4},
        {"numero": 3, "peso": 32.5, "reps": 6},
    ]


def test_rn_006_08_el_mismo_ejercicio_se_reconoce_aunque_se_escriba_distinto(api, ahora):
    api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=7), ejercicio="Press Inclinado")
    api.sesion_terminada([(35, 5)], inicio=ahora - timedelta(days=1), ejercicio="press inclinado ")

    ultima_vez = api.get(ARRANQUE).json()["ultima_vez"]

    assert list(ultima_vez) == ["press inclinado"]
    assert ultima_vez["press inclinado"]["series"][0]["peso"] == 35.0


def test_rn_006_09_las_series_sin_confirmar_no_cuentan(api, ahora):
    inicio = ahora - timedelta(days=1)
    sesion = api.sesion(inicio=inicio)
    ejercicio = api.ejercicio(sesion, momento=inicio)
    api.serie(ejercicio, numero=1, peso=30, reps=10, momento=inicio)
    api.serie(ejercicio, numero=2, peso=99, reps=1, confirmada=False, momento=inicio)
    api.terminar(sesion, inicio)

    series = api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]["series"]

    assert series == [{"numero": 1, "peso": 30.0, "reps": 10}]


def test_la_sesion_en_curso_no_cuenta_como_ultima_vez(api, ahora):
    api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=7))
    en_curso = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(en_curso), peso=50, reps=3)

    assert api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]["series"][0]["peso"] == 30.0


# --- RF-006-23 y RN-006-16: la nota de la última vez ------------------------


def test_ca_006_23a_la_nota_de_un_ejercicio_aparece_la_siguiente_vez(api, ahora):
    api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=7), nota_ejercicio="subir a 35")

    assert api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]["nota"] == "subir a 35"


def test_rn_006_16_si_la_sesion_mas_reciente_no_tiene_nota_no_se_muestra_una_vieja(api, ahora):
    api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=7), nota_ejercicio="subir a 35")
    api.sesion_terminada([(35, 5)], inicio=ahora - timedelta(days=1), nota_ejercicio="")

    assert api.get(ARRANQUE).json()["ultima_vez"]["press inclinado"]["nota"] == ""
