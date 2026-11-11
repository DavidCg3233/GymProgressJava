"""Progreso por la API: récords, semanas, grupos y vacío (T-004-04 a 07).

Spec 004 · RF-004-04, 05, 06, 11, 12 · RN-004-01 a 10 ·
CA-004-04a, 04b, 04c, 05a, 05b, 06a, 12a · plan 004, secciones 4.1 a 4.4.

"Hoy" es el jueves 26 de noviembre de 2026 a las 6 p. m., hora de Colombia.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from rutinas.models import Ejercicio, GrupoMuscular

from .conftest import BACKEND, nuevo_id

pytestmark = pytest.mark.django_db

URL = "/api/progreso/"
BOGOTA = ZoneInfo("America/Bogota")


def hora(dia, mes=11, h=18, minuto=0):
    return datetime(2026, mes, dia, h, minuto, tzinfo=BOGOTA)


@pytest.fixture
def jueves(reloj, api):
    reloj._ahora = hora(26)
    # Se vuelve a entrar: adelantar el reloj vencería el acceso de 7 días.
    api.client.force_login(api.cuenta, backend=BACKEND)
    return reloj


def progreso(api):
    respuesta = api.get(URL)
    assert respuesta.status_code == 200, respuesta.content
    return respuesta.json()


def records(api):
    return {record["nombre"]: record for record in progreso(api)["records"]}


def ejercicio_del_catalogo(api, clave):
    return Ejercicio.objects.get(usuario=api.cuenta, clave=clave)


# --- Vacío (RF-004-12) ------------------------------------------------------


def test_ca_004_12a_cuenta_nueva_sin_sesiones_esta_vacia(api, jueves):
    assert progreso(api) == {"vacio": True, "meta": None, "semanas": [], "grupos": [], "records": []}


def test_una_sesion_en_curso_no_cuenta_rn_004_01(api, jueves):
    sesion = api.sesion(inicio=hora(26, h=17))
    api.serie(api.ejercicio(sesion, momento=hora(26, h=17)), peso=50, reps=5, momento=hora(26, h=17))

    assert progreso(api)["vacio"] is True


def test_una_sesion_que_se_cerro_sola_a_las_2_horas_si_cuenta(api, jueves):
    sesion = api.sesion(inicio=hora(26, h=15))
    api.serie(api.ejercicio(sesion, momento=hora(26, h=15)), peso=50, reps=5, momento=hora(26, h=15))

    datos = progreso(api)

    assert datos["vacio"] is False
    assert datos["semanas"][-1]["sesiones"] == 1


# --- Récords (RF-004-04) ----------------------------------------------------


def test_ca_004_04a_record_por_la_api(api, jueves):
    api.sesion_terminada([(32.5, 8)], inicio=hora(2))
    api.sesion_terminada([(35, 5)], inicio=hora(9))
    api.sesion_terminada([(35, 6)], inicio=hora(16))
    api.sesion_terminada([(35, 6), (30, 15)], inicio=hora(23))

    assert records(api)["Press inclinado"] == {
        "clave": "press inclinado",
        "nombre": "Press inclinado",
        "peso": 35.0,
        "reps": 6,
        "fecha": "2026-11-16",
        "peso_corporal": False,
    }


def test_ca_004_04b_record_de_peso_corporal(api, jueves):
    api.sesion_terminada([(0, 8), (0, 10)], inicio=hora(23), ejercicio="Dominadas", grupo="Espalda")

    record = records(api)["Dominadas"]

    assert (record["peso"], record["reps"], record["peso_corporal"]) == (0.0, 10, True)


def test_ca_004_04c_el_record_no_mira_el_peso_de_la_rutina(api, jueves):
    api.sesion_terminada([(35, 6)], inicio=hora(16))
    press = ejercicio_del_catalogo(api, "press inclinado")
    rutina = api.put(
        f"/api/rutinas/{nuevo_id()}/",
        nombre="Pecho",
        dias=[1],
        ejercicios=[{"ejercicio": str(press.pk), "series": 3, "reps": 10, "peso": 20}],
    )
    assert rutina.status_code == 200

    assert (records(api)["Press inclinado"]["peso"], records(api)["Press inclinado"]["reps"]) == (35.0, 6)


def test_una_serie_sin_confirmar_no_es_record(api, jueves):
    sesion = api.sesion(inicio=hora(23))
    ejercicio = api.ejercicio(sesion, momento=hora(23))
    api.serie(ejercicio, numero=1, peso=30, reps=10, momento=hora(23))
    api.serie(ejercicio, numero=2, peso=100, reps=10, confirmada=False, momento=hora(23))
    api.terminar(sesion, hora(23))

    assert records(api)["Press inclinado"]["peso"] == 30.0


def test_rn_004_10_un_ejercicio_eliminado_conserva_su_record_y_su_nombre(api, jueves):
    api.sesion_terminada([(35, 6)], inicio=hora(16))
    press = ejercicio_del_catalogo(api, "press inclinado")
    assert api.delete(f"/api/catalogo/ejercicios/{press.pk}/").status_code == 200

    assert records(api)["Press inclinado"]["peso"] == 35.0


def test_un_ejercicio_renombrado_junta_sus_series_con_el_nombre_nuevo(api, jueves):
    api.sesion_terminada([(35, 6)], inicio=hora(16))
    press = ejercicio_del_catalogo(api, "press inclinado")
    api.put(f"/api/catalogo/ejercicios/{press.pk}/", nombre="Press inclinado con barra", grupo=str(press.grupo_id))
    api.sesion_terminada([(30, 8)], inicio=hora(23), ejercicio="Press inclinado con barra")

    todos = records(api)

    assert list(todos) == ["Press inclinado con barra"]
    assert todos["Press inclinado con barra"]["peso"] == 35.0


def test_los_records_van_por_nombre(api, jueves):
    api.sesion_terminada([(60, 5)], inicio=hora(23), ejercicio="Sentadilla", grupo="Pierna")
    api.sesion_terminada([(20, 10)], inicio=hora(24), ejercicio="Curl con barra", grupo="Bíceps")

    assert list(records(api)) == ["Curl con barra", "Sentadilla"]


# --- Semanas y meta (RF-004-05, 11) -----------------------------------------


def test_ca_004_05a_tres_de_cuatro_no_cumple(api, jueves):
    api.put("/api/progreso/meta/", meta=4)
    api.sesion_terminada([(30, 10)], inicio=hora(23), nombre="Pecho")
    api.sesion_terminada([(30, 10)], inicio=hora(24))  # libre
    api.sesion_terminada([(30, 10)], inicio=hora(25), nombre="Pierna")

    datos = progreso(api)

    assert datos["meta"] == 4
    assert len(datos["semanas"]) == 12
    assert datos["semanas"][-1] == {"inicio": "2026-11-23", "sesiones": 3, "cumple": False}
    assert datos["semanas"][0] == {"inicio": "2026-09-07", "sesiones": 0, "cumple": False}


def test_sin_meta_ninguna_semana_se_juzga(api, jueves):
    api.sesion_terminada([(30, 10)], inicio=hora(23))

    assert {semana["cumple"] for semana in progreso(api)["semanas"]} == {None}


def test_la_meta_de_hoy_juzga_todas_las_semanas(api, jueves):
    api.sesion_terminada([(30, 10)], inicio=hora(16))
    api.sesion_terminada([(30, 10)], inicio=hora(17))
    api.put("/api/progreso/meta/", meta=2)

    semanas = progreso(api)["semanas"]

    assert semanas[-2] == {"inicio": "2026-11-16", "sesiones": 2, "cumple": True}


def test_ca_004_05b_cuenta_para_la_semana_en_que_empezo(api, jueves):
    # Domingo 22 a las 11:30 p. m.; termina el lunes 23 a las 12:30 a. m.
    api.sesion_terminada([(30, 10)], inicio=hora(22, h=23, minuto=30))

    semanas = progreso(api)["semanas"]

    assert semanas[-2]["sesiones"] == 1
    assert semanas[-1]["sesiones"] == 0


def test_una_sesion_terminada_sin_series_confirmadas_no_suma(api, jueves):
    api.sesion_terminada([(30, 10)], inicio=hora(23))
    vacia = api.sesion(inicio=hora(24))
    api.serie(api.ejercicio(vacia, momento=hora(24)), confirmada=False, momento=hora(24))
    api.terminar(vacia, hora(24))

    assert progreso(api)["semanas"][-1]["sesiones"] == 1


# --- Series por grupo muscular (RF-004-06) ----------------------------------


def test_ca_004_06a_grupos_de_esta_semana_de_mayor_a_menor_con_ceros(api, jueves):
    api.sesion_terminada([(30, 10)] * 5, inicio=hora(23))
    api.sesion_terminada([(30, 10)] * 4, inicio=hora(25))
    api.sesion_terminada([(20, 10)] * 4, inicio=hora(24), ejercicio="Curl con barra", grupo="Bíceps")
    api.sesion_terminada([(60, 5)] * 3, inicio=hora(19), ejercicio="Sentadilla", grupo="Pierna")  # otra semana

    grupos = progreso(api)["grupos"]

    assert grupos[:2] == [{"nombre": "Pecho", "series": 9}, {"nombre": "Bíceps", "series": 4}]
    assert {"nombre": "Pierna", "series": 0} in grupos
    assert len(grupos) == 8
    assert [grupo["nombre"] for grupo in grupos[2:]] == ["Abdomen", "Espalda", "Hombro", "Pantorrilla", "Pierna", "Tríceps"]


def test_cambiar_un_ejercicio_de_grupo_mueve_sus_series(api, jueves):
    api.sesion_terminada([(30, 10)] * 3, inicio=hora(23))
    press = ejercicio_del_catalogo(api, "press inclinado")
    hombro = GrupoMuscular.objects.get(usuario=api.cuenta, clave="hombro")
    api.put(f"/api/catalogo/ejercicios/{press.pk}/", nombre=press.nombre, grupo=str(hombro.pk))

    grupos = {grupo["nombre"]: grupo["series"] for grupo in progreso(api)["grupos"]}

    assert (grupos["Hombro"], grupos["Pecho"]) == (3, 0)


def test_un_ejercicio_eliminado_cuenta_en_el_grupo_que_tenia(api, jueves):
    cardio = nuevo_id()
    api.put(f"/api/catalogo/grupos/{cardio}/", nombre="Cardio")
    bici = nuevo_id()
    api.put(f"/api/catalogo/ejercicios/{bici}/", nombre="Bici", grupo=cardio)
    api.sesion_terminada([(0, 20)] * 2, inicio=hora(23), ejercicio="Bici", grupo="Cardio")
    api.delete(f"/api/catalogo/ejercicios/{bici}/")
    assert api.delete(f"/api/catalogo/grupos/{cardio}/").status_code == 204

    grupos = {grupo["nombre"]: grupo["series"] for grupo in progreso(api)["grupos"]}

    assert grupos["Cardio"] == 2


# --- Evolución de un ejercicio (RF-004-09, T-004-08) ------------------------

EVOLUCION = "/api/progreso/evolucion/"


def test_ca_004_09a_un_punto_por_sesion_con_serie_mas_pesada_y_volumen(api, jueves):
    api.sesion_terminada([(30, 10), (32.5, 8), (32.5, 6)], inicio=hora(23))
    api.sesion_terminada([(35, 6)], inicio=hora(16))

    respuesta = api.get(EVOLUCION + "?clave=press inclinado")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "nombre": "Press inclinado",
        "peso_corporal": False,
        "puntos": [
            {"fecha": "2026-11-16", "pesada": 35.0, "reps_de_la_pesada": 6, "volumen": 210.0},
            {"fecha": "2026-11-23", "pesada": 32.5, "reps_de_la_pesada": 8, "volumen": 755.0},
        ],
    }


def test_evolucion_de_peso_corporal_lleva_reps(api, jueves):
    api.sesion_terminada([(0, 8), (0, 10)], inicio=hora(23), ejercicio="Dominadas", grupo="Espalda")

    datos = api.get(EVOLUCION + "?clave=dominadas").json()

    assert datos["peso_corporal"] is True
    assert datos["puntos"] == [{"fecha": "2026-11-23", "pesada": 0.0, "reps_de_la_pesada": 10, "volumen": 18}]


@pytest.mark.parametrize("consulta", ["?clave=sentadilla", "?clave=", "", "?clave=" + "x" * 500])
def test_evolucion_de_un_ejercicio_sin_series_responde_404(api, jueves, consulta):
    api.sesion_terminada([(30, 10)], inicio=hora(23))

    assert api.get(EVOLUCION + consulta).status_code == 404
