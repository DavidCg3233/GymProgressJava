"""API de rutinas (T-002-08, T-002-09).

Spec 002 · RF-002-01, 03, 04, 05, 06, 20, 21 · CA-002-01a, 03a, 06a, 21a,
CA-002-RN · plan 002, sección 4.4.
"""

from datetime import timedelta

import pytest

from rutinas.models import Ejercicio, Rutina

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db

RUTINAS = "/api/rutinas/"


def ej(api, clave):
    return str(Ejercicio.objects.get(usuario=api.cuenta, clave=clave).pk)


def previsto(api, clave, series=3, reps=10, peso=30):
    return {"ejercicio": ej(api, clave), "series": series, "reps": reps, "peso": peso}


def guardar(api, id=None, nombre="Pecho", dias=(), ejercicios=None):
    id = id or nuevo_id()
    ejercicios = ejercicios if ejercicios is not None else [previsto(api, "press inclinado")]
    return id, api.put(f"{RUTINAS}{id}/", nombre=nombre, dias=list(dias), ejercicios=ejercicios)


# --- RF-002-01, 04, 20: guardar y listar ------------------------------------


def test_ca_002_01a_crear_una_rutina_para_lunes_y_jueves(api):
    id, respuesta = guardar(api, dias=[4, 1], ejercicios=[previsto(api, "press inclinado", series=3, reps=10, peso=30)])

    assert respuesta.status_code == 200
    esperado = {
        "id": id,
        "nombre": "Pecho",
        "dias": [1, 4],
        "ejercicios": [
            {"ejercicio": ej(api, "press inclinado"), "nombre": "Press inclinado", "grupo": "Pecho", "series": 3, "reps": 10, "peso": 30.0}
        ],
    }
    assert respuesta.json() == {"rutina": esperado}
    assert api.get(RUTINAS).json() == {"rutinas": [esperado]}


def test_rf_002_20_los_ejercicios_quedan_en_el_orden_enviado(api):
    _, respuesta = guardar(api, ejercicios=[previsto(api, "fondos"), previsto(api, "press de banca"), previsto(api, "press inclinado")])

    assert [e["nombre"] for e in respuesta.json()["rutina"]["ejercicios"]] == ["Fondos", "Press de banca", "Press inclinado"]


def test_las_rutinas_se_listan_por_nombre(api):
    guardar(api, nombre="Pierna")
    guardar(api, nombre="Brazo")

    assert [r["nombre"] for r in api.get(RUTINAS).json()["rutinas"]] == ["Brazo", "Pierna"]


def test_guardar_dos_veces_la_misma_no_la_duplica(api):
    id, _ = guardar(api)

    guardar(api, id=id)

    assert Rutina.objects.filter(usuario=api.cuenta).count() == 1


# --- RF-002-05: modificar, todo o nada --------------------------------------


def test_modificar_reemplaza_nombre_dias_y_ejercicios(api):
    id, _ = guardar(api, dias=[1], ejercicios=[previsto(api, "press inclinado"), previsto(api, "fondos")])

    _, respuesta = guardar(api, id=id, nombre="Pecho y tríceps", dias=[3], ejercicios=[previsto(api, "fondos", series=4)])

    rutina = respuesta.json()["rutina"]
    assert (rutina["nombre"], rutina["dias"]) == ("Pecho y tríceps", [3])
    assert [(e["nombre"], e["series"]) for e in rutina["ejercicios"]] == [("Fondos", 4)]


def test_si_un_ejercicio_es_invalido_la_rutina_anterior_queda_intacta(api):
    id, _ = guardar(api, dias=[1], ejercicios=[previsto(api, "press inclinado")])

    _, respuesta = guardar(api, id=id, nombre="Otro", dias=[2], ejercicios=[previsto(api, "fondos"), previsto(api, "sentadilla", reps=101)])

    assert respuesta.status_code == 400
    intacta = api.get(RUTINAS).json()["rutinas"][0]
    assert (intacta["nombre"], intacta["dias"], [e["nombre"] for e in intacta["ejercicios"]]) == ("Pecho", [1], ["Press inclinado"])


# --- CA-002-03a y CA-002-RN: rechazos ---------------------------------------


@pytest.mark.parametrize(
    ("cambios", "campo", "mensaje"),
    [
        pytest.param({"nombre": ""}, "nombre", "Escribe el nombre de la rutina.", id="CA-002-03a sin nombre"),
        pytest.param({"nombre": "r" * 51}, "nombre", "El nombre de la rutina admite máximo 50 caracteres.", id="51 caracteres"),
        pytest.param({"ejercicios": []}, "ejercicios", "Agrega al menos un ejercicio.", id="CA-002-03a sin ejercicios"),
        pytest.param({"dias": [8]}, "dias", "Los días van de lunes (1) a domingo (7), sin repetir.", id="dia invalido"),
        pytest.param({"dias": "1"}, "dias", "Los días van de lunes (1) a domingo (7), sin repetir.", id="dias no es lista"),
    ],
)
def test_una_rutina_invalida_se_rechaza_indicando_el_campo(api, cambios, campo, mensaje):
    datos = {"nombre": "Pecho", "dias": [], "ejercicios": [previsto(api, "press inclinado")]} | cambios

    respuesta = api.put(f"{RUTINAS}{nuevo_id()}/", **datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": campo}


@pytest.mark.parametrize(
    ("cambios", "campo", "mensaje"),
    [
        pytest.param({"series": 0}, "series", "Las series previstas van de 1 a 10.", id="0 series"),
        pytest.param({"series": 11}, "series", "Las series previstas van de 1 a 10.", id="11 series"),
        pytest.param({"reps": 0}, "reps", "Las repeticiones deben estar entre 1 y 100.", id="0 reps"),
        pytest.param({"reps": 101}, "reps", "Las repeticiones deben estar entre 1 y 100.", id="101 reps"),
        pytest.param({"peso": -0.5}, "peso", "El peso debe estar entre 0 y 500 kg.", id="peso negativo"),
        pytest.param({"peso": 500.5}, "peso", "El peso debe estar entre 0 y 500 kg.", id="500,5 kg"),
        pytest.param({"peso": 30.3}, "peso", "El peso va de a 0,5 kg.", id="30,3 kg"),
    ],
)
def test_ca_002_rn_bordes_de_lo_previsto(api, cambios, campo, mensaje):
    _, respuesta = guardar(api, ejercicios=[previsto(api, "press inclinado") | cambios])

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": campo}


@pytest.mark.parametrize(("series", "reps", "peso"), [(1, 1, 0), (10, 100, 500)])
def test_ca_002_rn_los_limites_se_aceptan(api, series, reps, peso):
    _, respuesta = guardar(api, ejercicios=[previsto(api, "press inclinado", series=series, reps=reps, peso=peso)])

    assert respuesta.status_code == 200


def test_ca_002_rn_veinte_ejercicios_si_veintiuno_no(api):
    claves = list(Ejercicio.objects.filter(usuario=api.cuenta).values_list("clave", flat=True))[:21]

    assert guardar(api, nombre="Veinte", ejercicios=[previsto(api, c) for c in claves[:20]])[1].status_code == 200
    respuesta = guardar(api, nombre="Veintiuno", ejercicios=[previsto(api, c) for c in claves])[1]
    assert respuesta.json() == {"mensaje": "Una rutina admite máximo 20 ejercicios.", "campo": "ejercicios"}


def test_ca_002_rn_el_mismo_ejercicio_dos_veces_se_rechaza(api):
    _, respuesta = guardar(api, ejercicios=[previsto(api, "fondos"), previsto(api, "fondos")])

    assert respuesta.json() == {"mensaje": "Un ejercicio aparece una sola vez por rutina.", "campo": "ejercicios"}


def test_ca_002_rn_un_nombre_que_ya_tengo_se_rechaza(api):
    guardar(api, nombre="Pecho")

    _, respuesta = guardar(api, nombre="PECHO")

    assert respuesta.json() == {"mensaje": "Ya tienes una rutina con ese nombre.", "campo": "nombre"}


@pytest.mark.parametrize("ejercicio_dado", ["no-es-un-uuid", None, 5])
def test_un_ejercicio_que_no_esta_en_mi_catalogo_se_rechaza(api, ejercicio_dado):
    _, respuesta = guardar(api, ejercicios=[{"ejercicio": ejercicio_dado, "series": 3, "reps": 10, "peso": 30}])

    assert respuesta.json() == {"mensaje": "Ese ejercicio no está en tu catálogo.", "campo": "ejercicios"}


@pytest.mark.parametrize("cuerpo", [[1, 2], "texto", None])
def test_ejercicios_mal_formados_no_rompen_el_servidor(api, cuerpo):
    _, respuesta = guardar(api, ejercicios=cuerpo) if cuerpo is not None else guardar(api, ejercicios=[None])

    assert respuesta.status_code == 400


# --- RF-002-06: eliminar ----------------------------------------------------


def test_ca_002_06a_eliminar_una_rutina_no_toca_sus_sesiones(api, ahora):
    id, _ = guardar(api)
    sesiones = [api.sesion_terminada([(30, 10)], inicio=ahora - timedelta(days=d), nombre="Pecho") for d in (1, 2)]

    assert api.delete(f"{RUTINAS}{id}/").status_code == 204

    assert api.get(RUTINAS).json() == {"rutinas": []}
    assert [s["id"] for s in api.get("/api/sesiones/").json()["sesiones"]] == sesiones


# --- RF-002-21: duplicar ----------------------------------------------------


def test_ca_002_21a_duplicar_copia_los_ejercicios_y_deja_la_copia_sin_dias(api):
    id, _ = guardar(api, dias=[1, 4], ejercicios=[previsto(api, "press inclinado"), previsto(api, "fondos", series=4)])
    copia = nuevo_id()

    respuesta = api.client.post(f"{RUTINAS}{id}/duplicar/", data={"id_copia": copia}, content_type="application/json")

    assert respuesta.status_code == 200
    duplicada = respuesta.json()["rutina"]
    assert (duplicada["id"], duplicada["nombre"], duplicada["dias"]) == (copia, "Pecho (copia)", [])
    assert [(e["nombre"], e["series"]) for e in duplicada["ejercicios"]] == [("Press inclinado", 3), ("Fondos", 4)]


def test_duplicar_dos_veces_numera_la_copia(api):
    id, _ = guardar(api)
    for _ in range(2):
        api.client.post(f"{RUTINAS}{id}/duplicar/", data={"id_copia": nuevo_id()}, content_type="application/json")

    assert sorted(r["nombre"] for r in api.get(RUTINAS).json()["rutinas"]) == ["Pecho", "Pecho (copia 2)", "Pecho (copia)"]


# --- Lo ajeno no existe (RNF-ACC-06) ----------------------------------------


def test_otra_persona_no_ve_ni_toca_rutinas_ajenas(api, otra):
    id, _ = guardar(api)

    assert otra.get(RUTINAS).json() == {"rutinas": []}
    assert otra.put(f"{RUTINAS}{id}/", nombre="Mía", dias=[], ejercicios=[previsto(otra, "fondos")]).status_code == 404
    assert otra.delete(f"{RUTINAS}{id}/").status_code == 404
    duplicar = otra.client.post(f"{RUTINAS}{id}/duplicar/", data={"id_copia": nuevo_id()}, content_type="application/json")
    assert duplicar.status_code == 404
    assert Rutina.objects.get(pk=id).nombre == "Pecho"


def test_no_se_puede_meter_un_ejercicio_ajeno_en_mi_rutina(api, otra):
    _, respuesta = guardar(api, ejercicios=[previsto(otra, "fondos")])

    assert respuesta.json() == {"mensaje": "Ese ejercicio no está en tu catálogo.", "campo": "ejercicios"}
