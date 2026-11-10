"""Configuración para correr las pruebas.

Define valores de entorno ficticios y luego carga la configuración real,
para que las pruebas ejerciten el mismo archivo que usa producción.

Base de datos:
- Si el entorno define GP_DB_HOST (Docker Compose, revisiones automáticas),
  las pruebas usan PostgreSQL, igual que producción.
- Si no, usan SQLite en memoria: alcanza para las pruebas que no dependen
  de PostgreSQL y permite correrlas sin tener nada instalado.
  Las que sí dependen se marcan con `@pytest.mark.postgres` y se omiten.
"""

import os

USAR_POSTGRES = bool(os.environ.get("GP_DB_HOST", "").strip())

os.environ.setdefault("GP_SECRET_KEY", "clave-solo-para-pruebas-no-usar-en-produccion")
os.environ.setdefault("GP_ALLOWED_HOSTS", "testserver,localhost")
os.environ.setdefault("GP_DB_NAME", "gymprogress")
os.environ.setdefault("GP_DB_USER", "gymprogress")
os.environ.setdefault("GP_DB_PASSWORD", "solo-para-pruebas")
os.environ.setdefault("GP_DB_HOST", "localhost")

from .settings import *  # noqa: E402,F401,F403

if not USAR_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
