"""Lectura de la configuración desde variables de entorno.

Ningún secreto vive en el código ni en el repositorio (RNF-SEG-03): todo
valor sensible entra por aquí. Si falta uno obligatorio, el servidor no
arranca, en lugar de arrancar con un valor inseguro por defecto.
"""

import os

from django.core.exceptions import ImproperlyConfigured

_VALORES_VERDADEROS = frozenset({"1", "true", "si", "sí", "yes", "on"})


def obligatoria(nombre: str) -> str:
    """Devuelve la variable o detiene el arranque si falta o está vacía."""
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise ImproperlyConfigured(f"Falta la variable de entorno obligatoria {nombre}.")
    return valor


def opcional(nombre: str, por_defecto: str = "") -> str:
    """Devuelve la variable, o el valor por defecto si no está definida."""
    return os.environ.get(nombre, por_defecto).strip()


def booleana(nombre: str) -> bool:
    """Interpreta la variable como verdadero o falso. Ausente equivale a falso."""
    return opcional(nombre).lower() in _VALORES_VERDADEROS


def lista(nombre: str) -> list[str]:
    """Separa la variable por comas, descartando espacios y elementos vacíos."""
    return [parte.strip() for parte in opcional(nombre).split(",") if parte.strip()]
