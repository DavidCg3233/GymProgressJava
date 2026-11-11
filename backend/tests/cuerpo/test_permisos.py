"""El peso de una persona no lo ve ni lo toca nadie más (T-003-07).

RNF-ACC-06 · plan 003, sección 7.
"""

import pytest

from cuerpo.models import RegistroDePeso

pytestmark = pytest.mark.django_db

FECHA = "2026-11-10"


def test_la_misma_fecha_en_dos_cuentas_son_registros_distintos(api, otra):
    api.put(f"/api/peso/{FECHA}/", peso=79)
    otra.put(f"/api/peso/{FECHA}/", peso=60)

    assert [r["peso"] for r in api.get("/api/peso/").json()["registros"]] == [79.0]
    assert [r["peso"] for r in otra.get("/api/peso/").json()["registros"]] == [60.0]


def test_no_se_corrige_ni_se_borra_lo_ajeno(api, otra):
    otra.put(f"/api/peso/{FECHA}/", peso=60)

    assert api.delete(f"/api/peso/{FECHA}/").status_code == 404
    # Pesarse la misma fecha crea un registro propio: no pide reemplazar el de la otra persona.
    assert api.put(f"/api/peso/{FECHA}/", peso=79).status_code == 200
    assert RegistroDePeso.objects.get(usuario=otra.cuenta).peso == 60


def test_estatura_y_objetivo_son_de_cada_cuenta(api, otra):
    api.put("/api/peso/estatura/", estatura=175)
    api.put("/api/peso/objetivo/", objetivo=75)

    assert otra.get("/api/peso/").json()["estatura"] is None
    assert otra.get("/api/peso/").json()["objetivo"] is None


@pytest.mark.parametrize(
    ("metodo", "url", "datos"),
    [
        ("get", "/api/peso/", {}),
        ("put", f"/api/peso/{FECHA}/", {"peso": 79}),
        ("delete", f"/api/peso/{FECHA}/", {}),
        ("put", "/api/peso/estatura/", {"estatura": 175}),
        ("put", "/api/peso/objetivo/", {"objetivo": 75}),
    ],
)
def test_sin_acceso_no_se_puede_nada(anonimo, metodo, url, datos):
    respuesta = getattr(anonimo, metodo)(url, **datos) if datos else getattr(anonimo, metodo)(url)

    assert respuesta.status_code == 401
