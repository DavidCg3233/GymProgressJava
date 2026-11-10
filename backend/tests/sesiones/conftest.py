"""Herramientas compartidas por las pruebas de la API de sesiones."""

import json
import uuid
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

BACKEND = "cuentas.autenticacion.UsuarioOCorreo"
CONTRASENA = "Xk9!mQ2#vL"


class Api:
    """Un navegador con acceso vigente que habla JSON con el servidor."""

    def __init__(self, cuenta=None):
        self.client = Client()
        self.cuenta = cuenta
        if cuenta is not None:
            self.client.force_login(cuenta, backend=BACKEND)

    def get(self, url):
        return self.client.get(url)

    def put(self, url, **datos):
        return self.client.put(url, data=json.dumps(datos), content_type="application/json")

    def delete(self, url, **datos):
        return self.client.delete(url, data=json.dumps(datos), content_type="application/json")

    # --- Atajos para armar el escenario de una prueba ---

    def sesion(self, id=None, inicio=None, fin=None, nombre="", nota=""):
        id = id or nuevo_id()
        inicio = inicio or timezone.now()
        respuesta = self.put(
            f"/api/sesiones/{id}/",
            nombre=nombre,
            inicio=inicio.isoformat(),
            fin=fin.isoformat() if fin else None,
            nota=nota,
        )
        assert respuesta.status_code == 200, respuesta.content
        return id

    def ejercicio(self, sesion, id=None, nombre="Press inclinado", grupo="Pecho", orden=1, nota="", momento=None):
        id = id or nuevo_id()
        respuesta = self.put(
            f"/api/sesiones/{sesion}/ejercicios/{id}/",
            nombre=nombre,
            grupo=grupo,
            orden=orden,
            nota=nota,
            momento=(momento or timezone.now()).isoformat(),
        )
        assert respuesta.status_code == 200, respuesta.content
        return id

    def serie(self, ejercicio, numero=1, peso=30, reps=10, confirmada=True, id=None, momento=None):
        id = id or nuevo_id()
        respuesta = self.put(
            f"/api/series/{id}/",
            ejercicio=ejercicio,
            numero=numero,
            peso=peso,
            reps=reps,
            confirmada=confirmada,
            momento=(momento or timezone.now()).isoformat(),
        )
        assert respuesta.status_code == 200, respuesta.content
        return id

    def terminar(self, sesion, inicio, fin=None, nombre="", nota=""):
        fin = fin or inicio + timedelta(hours=1)
        return self.put(
            f"/api/sesiones/{sesion}/", nombre=nombre, inicio=inicio.isoformat(), fin=fin.isoformat(), nota=nota
        )

    def sesion_terminada(self, series, inicio, nombre="", ejercicio="Press inclinado", grupo="Pecho", nota_ejercicio=""):
        """Crea y termina una sesión con un ejercicio y las series dadas: [(peso, reps), ...]."""
        sesion = self.sesion(inicio=inicio, nombre=nombre)
        id_ejercicio = self.ejercicio(sesion, nombre=ejercicio, grupo=grupo, nota=nota_ejercicio, momento=inicio)
        for numero, (peso, reps) in enumerate(series, start=1):
            self.serie(id_ejercicio, numero=numero, peso=peso, reps=reps, momento=inicio)
        assert self.terminar(sesion, inicio, nombre=nombre).status_code == 200
        return sesion


def nuevo_id() -> str:
    return str(uuid.uuid4())


def crear_cuenta(usuario="davidc"):
    return get_user_model().objects.create_user(
        usuario=usuario, correo=f"{usuario}@ejemplo.com", nombre=usuario.capitalize(), password=CONTRASENA
    )


@pytest.fixture
def cuenta(db):
    return crear_cuenta()


@pytest.fixture
def api(cuenta):
    return Api(cuenta)


@pytest.fixture
def otra(db):
    """Una segunda persona, para comprobar que no ve ni toca lo ajeno (RNF-ACC-06)."""
    return Api(crear_cuenta("andrea"))


@pytest.fixture
def anonimo(db):
    return Api()


class Reloj:
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
    return reloj


@pytest.fixture
def ahora(reloj):
    return reloj()
