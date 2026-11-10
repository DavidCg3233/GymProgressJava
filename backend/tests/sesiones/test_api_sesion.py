"""Guardar, terminar y cerrar una sesión (T-006-18, T-006-20).

Spec 006 · RF-006-02, 07, 08, 19, 20, 21, 22.
"""

from datetime import timedelta

import pytest

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db


def url(id):
    return f"/api/sesiones/{id}/"


# --- RF-006-20: empezar una sesión libre ------------------------------------


def test_empezar_una_sesion_libre_la_deja_en_curso_y_sin_ejercicios(api, ahora):
    id = nuevo_id()

    respuesta = api.put(url(id), nombre="", inicio=ahora.isoformat(), fin=None, nota="")

    assert respuesta.status_code == 200
    sesion = respuesta.json()["sesion"]
    assert sesion["id"] == id
    assert sesion["en_curso"] is True
    assert sesion["fin"] is None
    assert sesion["ejercicios"] == []


def test_enviar_dos_veces_la_misma_sesion_no_la_duplica(api, ahora):
    id = api.sesion(inicio=ahora)

    api.sesion(id=id, inicio=ahora)

    assert api.get(url(id)).status_code == 200
    assert len(api.get("/api/sesiones/").json()["sesiones"]) == 0  # sigue en curso, no hay dos


# --- RF-006-02: una sola sesión en curso ------------------------------------


def test_ca_006_02a_con_una_sesion_en_curso_no_se_puede_empezar_otra(api, ahora):
    en_curso = api.sesion(inicio=ahora)

    respuesta = api.put(url(nuevo_id()), nombre="", inicio=ahora.isoformat(), fin=None, nota="")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"mensaje": "Ya tienes una sesión en curso.", "sesion_en_curso": en_curso}


def test_la_sesion_en_curso_de_otra_persona_no_me_impide_empezar_la_mia(api, otra, ahora):
    otra.sesion(inicio=ahora)

    assert api.put(url(nuevo_id()), nombre="", inicio=ahora.isoformat(), fin=None, nota="").status_code == 200


# --- RF-006-07, 21, 22: terminar --------------------------------------------


def test_ca_006_20a_terminar_sin_nombre_la_llama_sesion_libre(api, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion, nombre="Dominadas", grupo="Espalda")
    api.serie(ejercicio, peso=0, reps=8)

    respuesta = api.terminar(sesion, ahora)

    terminada = respuesta.json()["sesion"]
    assert terminada["nombre"] == "Sesión libre"
    assert terminada["en_curso"] is False
    assert terminada["ejercicios"][0]["series"] == [
        {"id": terminada["ejercicios"][0]["series"][0]["id"], "numero": 1, "peso": 0.0, "reps": 8, "confirmada": True}
    ]


def test_ca_006_21a_y_22a_terminar_con_nombre_y_nota_los_conserva(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))

    terminada = api.terminar(sesion, ahora, nombre="Hotel Bogotá", nota="dormí mal").json()["sesion"]

    assert terminada["nombre"] == "Hotel Bogotá"
    assert terminada["nota"] == "dormí mal"
    assert api.get(url(sesion)).json()["sesion"]["nota"] == "dormí mal"


def test_tras_terminar_se_puede_empezar_otra(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))
    api.terminar(sesion, ahora)

    assert api.put(url(nuevo_id()), nombre="", inicio=ahora.isoformat(), fin=None, nota="").status_code == 200


def test_una_sesion_terminada_no_se_puede_reabrir(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))
    api.terminar(sesion, ahora)

    respuesta = api.put(url(sesion), nombre="", inicio=ahora.isoformat(), fin=None, nota="")

    assert respuesta.status_code == 409
    assert respuesta.json()["mensaje"] == "Esta sesión ya terminó y no se puede modificar."


def test_reenviar_el_cierre_de_una_sesion_ya_terminada_no_es_un_error(api, ahora):
    # La cola de pendientes puede repetir un envío si no supo que llegó.
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))
    primera = api.terminar(sesion, ahora, nota="dormí mal").json()

    segunda = api.terminar(sesion, ahora, nota="dormí mal")

    assert segunda.status_code == 200
    assert segunda.json() == primera


# --- RF-006-19: sesión sin series confirmadas -------------------------------


def test_ca_006_19a_terminar_sin_series_confirmadas_descarta_la_sesion(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion), confirmada=False)

    respuesta = api.terminar(sesion, ahora)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"sesion": None, "descartada": True}
    assert api.get(url(sesion)).status_code == 404
    assert api.get("/api/sesiones/").json()["sesiones"] == []


# --- RF-006-08: cierre automático a las 2 horas -----------------------------


def test_ca_006_08a_pasadas_2_horas_la_sesion_aparece_terminada_con_sus_series(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    for numero in range(1, 6):
        api.serie(ejercicio, numero=numero)

    reloj.avanzar(hours=2, minutes=1)

    cerrada = api.get(url(sesion)).json()["sesion"]
    assert cerrada["en_curso"] is False
    assert cerrada["fin"] == (ahora + timedelta(hours=2)).isoformat()  # RN-006-12
    assert len(cerrada["ejercicios"][0]["series"]) == 5
    # ...y ya se puede empezar una nueva.
    assert api.put(url(nuevo_id()), nombre="", inicio=reloj().isoformat(), fin=None, nota="").status_code == 200


def test_un_minuto_antes_de_las_2_horas_sigue_en_curso(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))

    reloj.avanzar(hours=1, minutes=59)

    assert api.get(url(sesion)).json()["sesion"]["en_curso"] is True


def test_una_sesion_vencida_sin_series_confirmadas_se_descarta_sola(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)

    reloj.avanzar(hours=3)

    assert api.get(url(sesion)).status_code == 404


def test_un_cierre_enviado_tarde_no_puede_superar_las_2_horas(api, ahora):
    # Sin conexión, el celular pudo terminarla a mano más tarde de lo permitido.
    inicio = ahora - timedelta(hours=5)
    sesion = api.sesion(inicio=inicio)
    api.serie(api.ejercicio(sesion, momento=inicio), momento=inicio)

    terminada = api.terminar(sesion, inicio, fin=inicio + timedelta(hours=4)).json()["sesion"]

    assert terminada["fin"] == (inicio + timedelta(hours=2)).isoformat()


def test_una_sesion_empezada_sin_conexion_hace_3_horas_se_acepta_al_sincronizar(api, ahora):
    # RF-006-17: no se rechaza, porque el celular aún tiene series por enviar.
    inicio = ahora - timedelta(hours=3)

    respuesta = api.put(url(nuevo_id()), nombre="", inicio=inicio.isoformat(), fin=None, nota="")

    assert respuesta.status_code == 200
    assert respuesta.json()["sesion"]["en_curso"] is False  # para el servidor ya cumplió sus 2 horas


# --- Validación (RNF-SEG-04) ------------------------------------------------


@pytest.mark.parametrize(
    ("cambios", "campo", "mensaje"),
    [
        ({"inicio": "ayer"}, "inicio", "La hora de inicio no es válida."),
        ({"inicio": None}, "inicio", "La hora de inicio no es válida."),
        ({"inicio": "2026-11-09T18:00:00"}, "inicio", "La hora de inicio no es válida."),
        ({"nota": "a" * 281}, "nota", "La nota admite máximo 280 caracteres."),
        ({"nombre": "n" * 51}, "nombre", "El nombre admite máximo 50 caracteres."),
    ],
)
def test_datos_invalidos_se_rechazan_indicando_el_campo(api, ahora, cambios, campo, mensaje):
    datos = {"nombre": "", "inicio": ahora.isoformat(), "fin": None, "nota": ""} | cambios

    respuesta = api.put(url(nuevo_id()), **datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": campo}


def test_el_fin_no_puede_ser_anterior_al_inicio(api, ahora):
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))

    respuesta = api.terminar(sesion, ahora, fin=ahora - timedelta(minutes=1))

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "La sesión no puede terminar antes de empezar.", "campo": "fin"}


def test_un_identificador_que_no_es_uuid_no_existe(api):
    assert api.get("/api/sesiones/123/").status_code == 404
