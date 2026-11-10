"""Configuración para probar el servidor en tu equipo, sin Docker ni PostgreSQL.

    python manage.py migrate --settings=config.settings_local
    python manage.py createsuperuser --settings=config.settings_local
    python manage.py runserver --settings=config.settings_local

Usa un archivo SQLite (`local.sqlite3`, ignorado por Git). Sirve para ver la
app funcionando; lo que dependa de PostgreSQL se prueba en Docker o en
GitHub Actions. NUNCA se usa en el servidor real.
"""

import os

# Valores fijos y sin valor fuera de tu equipo: aquí no hay nada que proteger.
os.environ.setdefault("GP_SECRET_KEY", "clave-local-solo-para-desarrollo-no-usar-en-el-servidor")
os.environ.setdefault("GP_DEBUG", "1")
os.environ.setdefault("GP_ALLOWED_HOSTS", "localhost,127.0.0.1")
os.environ.setdefault("GP_DB_NAME", "no-se-usa")
os.environ.setdefault("GP_DB_USER", "no-se-usa")
os.environ.setdefault("GP_DB_PASSWORD", "no-se-usa")
os.environ.setdefault("GP_DB_HOST", "no-se-usa")

from .settings import *  # noqa: E402,F401,F403
from .settings import BASE_DIR  # noqa: E402

# En desarrollo la pantalla corre en el puerto 5173 y le reenvía las peticiones
# a este servidor. Para la protección CSRF eso es "otro origen", así que hay que
# declararlo de confianza. En producción ambos comparten dominio y no hace falta.
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "local.sqlite3",
    }
}
