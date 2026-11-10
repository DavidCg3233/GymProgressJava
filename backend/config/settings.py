"""Configuración del servidor de GymProgress.

Todo lo que cambia entre equipos o es secreto se lee del entorno
(ver `entorno.py` y `.env.example`). Aquí no hay ningún valor sensible.
"""

from pathlib import Path

from . import entorno

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad -------------------------------------------------------------

SECRET_KEY = entorno.obligatoria("GP_SECRET_KEY")

# Apagada salvo que se pida de forma explícita en desarrollo (RNF-SEG-08, RNF-SEG-09).
DEBUG = entorno.booleana("GP_DEBUG")

ALLOWED_HOSTS = entorno.lista("GP_ALLOWED_HOSTS")

# --- Aplicaciones ----------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cuentas",
]

# --- Cuentas y contraseñas -------------------------------------------------

AUTH_USER_MODEL = "cuentas.Usuario"

# RNF-SEG-01: cifrado de una vía con Argon2. Nunca se guarda la contraseña.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# RNF-SEG-10: mínimo 10 caracteres, y además que no sea adivinable.
LARGO_MINIMO_DE_CONTRASENA = 10

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": LARGO_MINIMO_DE_CONTRASENA},
    },
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {"user_attributes": ("usuario", "correo", "nombre")},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# RNF-ACC-01: se entra con el nombre de usuario o con el correo.
AUTHENTICATION_BACKENDS = ["cuentas.autenticacion.UsuarioOCorreo"]

# --- Acceso recordado (RNF-ACC-02, RNF-ACC-03) -----------------------------

# 7 días, renovados con cada uso: solo se pide la contraseña tras 7 días sin abrir la app.
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True

# La cookie no la puede leer código de la página, solo viaja por HTTPS y
# otros sitios no pueden usarla para enviar acciones. En desarrollo (DEBUG)
# se permite HTTP, porque en el equipo no hay certificado.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Base de datos ---------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": entorno.obligatoria("GP_DB_NAME"),
        "USER": entorno.obligatoria("GP_DB_USER"),
        "PASSWORD": entorno.obligatoria("GP_DB_PASSWORD"),
        "HOST": entorno.obligatoria("GP_DB_HOST"),
        "PORT": entorno.opcional("GP_DB_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Idioma y hora (RNF-USA-05) --------------------------------------------

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos ----------------------------------------------------

STATIC_URL = "static/"
