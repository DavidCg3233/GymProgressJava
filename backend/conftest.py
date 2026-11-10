"""Configuración compartida de las pruebas."""

import pytest
from django.conf import settings


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "postgres: la prueba depende de PostgreSQL; se omite cuando se corre con SQLite.",
    )


def pytest_collection_modifyitems(config, items):
    if getattr(settings, "USAR_POSTGRES", False):
        return
    omitir = pytest.mark.skip(reason="Requiere PostgreSQL: correr dentro de Docker Compose.")
    for item in items:
        if "postgres" in item.keywords:
            item.add_marker(omitir)
