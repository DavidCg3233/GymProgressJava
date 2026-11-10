"""La configuración se lee de variables de entorno, nunca del código (RNF-SEG-03)."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from config import entorno


def test_obligatoria_devuelve_el_valor_definido(monkeypatch):
    monkeypatch.setenv("GP_PRUEBA", "valor")

    assert entorno.obligatoria("GP_PRUEBA") == "valor"


@pytest.mark.parametrize("valor", [None, "", "   "])
def test_obligatoria_falla_si_falta_o_esta_vacia(monkeypatch, valor):
    if valor is None:
        monkeypatch.delenv("GP_PRUEBA", raising=False)
    else:
        monkeypatch.setenv("GP_PRUEBA", valor)

    with pytest.raises(ImproperlyConfigured, match="GP_PRUEBA"):
        entorno.obligatoria("GP_PRUEBA")


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [("1", True), ("true", True), ("True", True), ("si", True), ("0", False), ("false", False), ("", False)],
)
def test_booleana_interpreta_los_valores_usuales(monkeypatch, valor, esperado):
    monkeypatch.setenv("GP_PRUEBA", valor)

    assert entorno.booleana("GP_PRUEBA") is esperado


def test_booleana_usa_falso_si_no_esta_definida(monkeypatch):
    monkeypatch.delenv("GP_PRUEBA", raising=False)

    assert entorno.booleana("GP_PRUEBA") is False


def test_lista_separa_por_comas_e_ignora_espacios_y_vacios(monkeypatch):
    monkeypatch.setenv("GP_PRUEBA", " a.com, b.com ,, ")

    assert entorno.lista("GP_PRUEBA") == ["a.com", "b.com"]


def test_lista_vacia_si_no_esta_definida(monkeypatch):
    monkeypatch.delenv("GP_PRUEBA", raising=False)

    assert entorno.lista("GP_PRUEBA") == []
