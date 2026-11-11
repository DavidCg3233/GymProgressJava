"""Peso corporal por la API (T-003-04 a 06).

Spec 003 · RF-003-01 a 13 · CA-003-01a, 02a, 05a, 08a, 09a, 10a, 11a, 13a · plan 003, sección 4.2.

"Hoy" es el miércoles 11 de noviembre de 2026 a mediodía, hora de Colombia. Estatura base: 175 cm.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from cuerpo.models import RegistroDePeso

from .conftest import BACKEND

pytestmark = pytest.mark.django_db

URL = "/api/peso/"
HOY = "2026-11-11"
AYER = "2026-11-10"


@pytest.fixture(autouse=True)
def miercoles(reloj, api):
    reloj._ahora = datetime(2026, 11, 11, 12, tzinfo=ZoneInfo("America/Bogota"))
    api.client.force_login(api.cuenta, backend=BACKEND)
    return reloj


def pesar(api, fecha, peso, **extra):
    return api.put(f"{URL}{fecha}/", peso=peso, **extra)


def datos(api):
    respuesta = api.get(URL)
    assert respuesta.status_code == 200, respuesta.content
    return respuesta.json()


# --- Registrar, reemplazar, corregir y eliminar (T-003-04) ------------------


def test_rf_003_01_registrar_un_peso(api):
    respuesta = pesar(api, HOY, 79)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"registro": {"fecha": HOY, "peso": 79.0}}
    assert datos(api)["registros"] == [{"fecha": HOY, "peso": 79.0}]


def test_ca_003_02a_el_mismo_dia_pide_confirmacion_y_luego_reemplaza(api):
    pesar(api, HOY, 79)

    sin_permiso = pesar(api, HOY, 78.5)
    assert sin_permiso.status_code == 409
    assert sin_permiso.json() == {"mensaje": "Ya registraste 79,0 kg ese día.", "peso": 79.0}
    assert datos(api)["registros"] == [{"fecha": HOY, "peso": 79.0}]

    assert pesar(api, HOY, 78.5, reemplazar=True).status_code == 200
    assert datos(api)["registros"] == [{"fecha": HOY, "peso": 78.5}]


def test_ca_003_10a_corregir_un_registro_recalcula_todo(api):
    pesar(api, AYER, 97)
    pesar(api, HOY, 79.5)

    assert pesar(api, AYER, 79, reemplazar=True).status_code == 200

    resultado = datos(api)
    assert resultado["registros"] == [{"fecha": HOY, "peso": 79.5}, {"fecha": AYER, "peso": 79.0}]
    assert resultado["resumen"]["cambio"] == {"kg": 0.5, "direccion": "subio"}


def test_ca_003_11a_eliminar_el_mas_reciente(api):
    pesar(api, "2026-11-09", 81)
    pesar(api, AYER, 80)
    pesar(api, HOY, 79)

    assert api.delete(f"{URL}{HOY}/").status_code == 204

    resultado = datos(api)
    assert len(resultado["registros"]) == 2
    assert resultado["resumen"]["actual"] == 80.0


def test_eliminar_un_dia_sin_registro_responde_404(api):
    assert api.delete(f"{URL}{HOY}/").status_code == 404


@pytest.mark.parametrize(
    ("fecha", "peso", "campo", "mensaje"),
    [
        (HOY, 19.9, "peso", "El peso va de 20 a 300 kg, con un decimal."),
        (HOY, 300.1, "peso", "El peso va de 20 a 300 kg, con un decimal."),
        (HOY, None, "peso", "Escribe tu peso."),
        ("2026-11-12", 79, "fecha", "La fecha no puede ser futura."),
    ],
)
def test_ca_003_13a_datos_fuera_de_rango_se_rechazan(api, fecha, peso, campo, mensaje):
    respuesta = pesar(api, fecha, peso)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "campo": campo}
    assert RegistroDePeso.objects.count() == 0


@pytest.mark.parametrize("fecha", ["2026-02-30", "11-11-2026", "hoy", "2026-11-11x"])
def test_una_fecha_mal_escrita_en_la_direccion_responde_404(api, fecha):
    assert pesar(api, fecha, 79).status_code == 404


def test_reemplazar_debe_ser_si_o_no(api):
    pesar(api, HOY, 79)

    assert pesar(api, HOY, 78, reemplazar="si").status_code == 400


# --- Estatura y objetivo (T-003-05) -----------------------------------------


def test_rf_003_12_fijar_y_cambiar_la_estatura(api):
    assert api.put(f"{URL}estatura/", estatura=175).json() == {"estatura": 175}
    assert api.put(f"{URL}estatura/", estatura=176).json() == {"estatura": 176}

    api.cuenta.refresh_from_db()
    assert api.cuenta.estatura_cm == 176


@pytest.mark.parametrize("valor", [99, 251, 1.75, "175", None])
def test_ca_003_13a_estatura_fuera_de_rango(api, valor):
    respuesta = api.put(f"{URL}estatura/", estatura=valor)

    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": "La estatura va en centímetros, de 100 a 250.", "campo": "estatura"}


def test_fijar_y_quitar_el_objetivo(api):
    assert api.put(f"{URL}objetivo/", objetivo=75).json() == {"objetivo": 75.0}
    assert api.put(f"{URL}objetivo/", objetivo=None).json() == {"objetivo": None}

    api.cuenta.refresh_from_db()
    assert api.cuenta.peso_objetivo is None


@pytest.mark.parametrize("valor", [19.9, 300.1])
def test_objetivo_fuera_de_rango(api, valor):
    respuesta = api.put(f"{URL}objetivo/", objetivo=valor)

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == "objetivo"


def test_sin_el_campo_se_rechaza(api):
    assert api.put(f"{URL}estatura/").status_code == 400
    assert api.put(f"{URL}objetivo/").status_code == 400


# --- Historial y resumen (T-003-06) -----------------------------------------


def test_sin_registros_no_hay_resumen(api):
    assert datos(api) == {"estatura": None, "objetivo": None, "registros": [], "resumen": None}


def test_ca_003_01a_peso_actual_cambio_e_imc(api):
    api.put(f"{URL}estatura/", estatura=175)
    pesar(api, AYER, 80)
    pesar(api, HOY, 79)

    assert datos(api)["resumen"] == {
        "actual": 79.0,
        "fecha": HOY,
        "cambio": {"kg": 1.0, "direccion": "bajo"},
        "imc": {"valor": 25.8, "categoria": "Sobrepeso"},
        "objetivo": None,
    }


def test_con_un_solo_registro_no_hay_cambio(api):
    pesar(api, HOY, 79)

    assert datos(api)["resumen"]["cambio"] is None


def test_ca_003_05a_sin_estatura_no_hay_imc(api):
    pesar(api, AYER, 80)
    pesar(api, HOY, 79)

    resumen = datos(api)["resumen"]

    assert resumen["imc"] is None
    assert resumen["cambio"] == {"kg": 1.0, "direccion": "bajo"}


def test_ca_003_08a_faltan_4_por_bajar(api):
    pesar(api, AYER, 80)
    pesar(api, HOY, 79)
    api.put(f"{URL}objetivo/", objetivo=75)

    assert datos(api)["resumen"]["objetivo"] == {"faltan": 4.0, "direccion": "bajar", "alcanzado": False}


def test_ca_003_09a_objetivo_alcanzado(api):
    pesar(api, AYER, 80)
    api.put(f"{URL}objetivo/", objetivo=75)
    pesar(api, HOY, 74.8)

    assert datos(api)["resumen"]["objetivo"]["alcanzado"] is True


def test_rf_003_06_historial_del_mas_reciente_al_mas_antiguo(api):
    for fecha, peso in [(AYER, 80), ("2026-10-01", 83), (HOY, 79)]:
        pesar(api, fecha, peso)

    assert [registro["fecha"] for registro in datos(api)["registros"]] == [HOY, AYER, "2026-10-01"]


def test_el_actual_es_el_de_fecha_mas_reciente_no_el_ultimo_escrito(api):
    pesar(api, HOY, 79)
    pesar(api, "2026-10-01", 83)  # se registra después un peso viejo

    assert datos(api)["resumen"]["actual"] == 79.0
