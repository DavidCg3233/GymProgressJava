"""Herramientas compartidas por las pruebas de cuentas."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

CONTRASENA = "Xk9!mQ2#vL"


@pytest.fixture
def cuenta(db):
    return get_user_model().objects.create_user(
        usuario="davidc",
        correo="david@ejemplo.com",
        nombre="David",
        password=CONTRASENA,
    )


class Reloj:
    """Reloj que las pruebas pueden adelantar, para no esperar días de verdad."""

    def __init__(self, ahora):
        self._ahora = ahora

    def __call__(self):
        return self._ahora

    def avanzar(self, **cuanto):
        self._ahora += timedelta(**cuanto)


@pytest.fixture
def reloj(monkeypatch):
    reloj = Reloj(timezone.now())
    monkeypatch.setattr(timezone, "now", reloj)
    # django-axes guarda su propia referencia a `now`; también hay que cambiarla.
    monkeypatch.setattr("axes.attempts.now", reloj)
    monkeypatch.setattr("axes.handlers.proxy.now", reloj)
    return reloj
