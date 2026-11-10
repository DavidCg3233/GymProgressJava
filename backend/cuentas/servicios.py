"""Operaciones sobre cuentas: invitar, restablecer y cambiar la contraseña.

Las usan por igual el panel del dueño y la API, para que la regla esté
escrita una sola vez.
"""

import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# 12 bytes al azar dan 16 caracteres: imposible de adivinar en la práctica.
_BYTES_DE_CONTRASENA_TEMPORAL = 12


class CambioDeContrasenaRechazado(Exception):
    """La contraseña no se cambió. `mensaje` es lo que ve el usuario."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


def invitar(usuario: str, correo: str, nombre: str):
    """Crea una cuenta con contraseña temporal. Devuelve la cuenta y esa contraseña (RNF-ACC-05).

    La contraseña temporal solo existe en este valor de retorno: en la base
    queda cifrada y no se puede volver a consultar.
    """
    temporal = _contrasena_temporal()
    cuenta = get_user_model().objects.create_user(
        usuario=usuario,
        correo=correo,
        nombre=nombre,
        password=temporal,
        debe_cambiar_contrasena=True,
    )
    return cuenta, temporal


def restablecer_contrasena(cuenta) -> str:
    """Reemplaza la contraseña por una temporal y obliga a cambiarla (RNF-ACC-09)."""
    temporal = _contrasena_temporal()
    cuenta.set_password(temporal)
    cuenta.debe_cambiar_contrasena = True
    cuenta.save(update_fields=["password", "debe_cambiar_contrasena"])
    return temporal


def cambiar_contrasena(cuenta, actual: str, nueva: str) -> None:
    """Cambia la contraseña de quien demuestra conocer la actual (RNF-ACC-08)."""
    if not cuenta.check_password(actual):
        raise CambioDeContrasenaRechazado("La contraseña actual no es correcta.")
    if nueva == actual:
        raise CambioDeContrasenaRechazado("La contraseña nueva debe ser distinta de la actual.")
    try:
        validate_password(nueva, user=cuenta)
    except ValidationError as error:
        raise CambioDeContrasenaRechazado(" ".join(error.messages)) from error

    cuenta.set_password(nueva)
    cuenta.debe_cambiar_contrasena = False
    cuenta.save(update_fields=["password", "debe_cambiar_contrasena"])


def _contrasena_temporal() -> str:
    return secrets.token_urlsafe(_BYTES_DE_CONTRASENA_TEMPORAL)
