"""Entrar, salir, consultar el estado del acceso y cambiar la contraseña."""

import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from . import servicios

# Un solo mensaje para todo rechazo: no revela si falló el usuario, la
# contraseña o si la cuenta está desactivada (RNF-SEG-09).
MENSAJE_DE_RECHAZO = "Usuario o contraseña incorrectos."

# RNF-ACC-07. Se muestra igual para cuentas que existen y que no.
MENSAJE_DE_BLOQUEO = "Demasiados intentos. Espera 15 minutos e inténtalo de nuevo."

MENSAJE_SIN_ACCESO = "Entra con tu cuenta para continuar."
MENSAJE_DE_DATOS_INCOMPLETOS = "Escribe la contraseña actual y la nueva."


@require_GET
@ensure_csrf_cookie
def estado(request: HttpRequest) -> JsonResponse:
    """Dice si hay acceso vigente. También entrega el token de protección CSRF."""
    cuenta = request.user if request.user.is_authenticated else None
    return JsonResponse(
        {
            "autenticado": cuenta is not None,
            "cuenta": _datos_de(cuenta) if cuenta else None,
        }
    )


@require_POST
def entrar(request: HttpRequest) -> JsonResponse:
    datos = _leer_textos(request, "identificador", "contrasena")
    identificador, contrasena = datos or ("", "")
    # Lo recuerda la petición para que el contador de intentos sepa a quién atribuirlos.
    request.identificador_de_acceso = identificador

    cuenta = authenticate(request, username=identificador, password=contrasena)
    if cuenta is None:
        # Si además la cuenta quedó bloqueada, `respuesta_de_bloqueo` reemplaza esta respuesta.
        return _rechazo(MENSAJE_DE_RECHAZO)

    # `login` estrena identificador de sesión: nadie puede fijarlo de antemano.
    login(request, cuenta)
    return JsonResponse({"cuenta": _datos_de(cuenta)})


@require_POST
def salir(request: HttpRequest) -> HttpResponse:
    """Borra la sesión en el servidor: la cookie anterior deja de servir (RNF-ACC-04)."""
    logout(request)
    return HttpResponse(status=204)


@require_POST
def cambiar_contrasena(request: HttpRequest) -> HttpResponse:
    """Cambia la contraseña de la cuenta en sesión (RNF-ACC-08, RNF-ACC-09)."""
    if not request.user.is_authenticated:
        return _rechazo(MENSAJE_SIN_ACCESO, status=401)

    datos = _leer_textos(request, "actual", "nueva")
    if datos is None:
        return _rechazo(MENSAJE_DE_DATOS_INCOMPLETOS)
    actual, nueva = datos

    try:
        servicios.cambiar_contrasena(request.user, actual, nueva)
    except servicios.CambioDeContrasenaRechazado as error:
        return _rechazo(error.mensaje)

    # Este navegador sigue dentro; las sesiones abiertas en otros dejan de valer.
    update_session_auth_hash(request, request.user)
    return HttpResponse(status=204)


def respuesta_de_bloqueo(request: HttpRequest, respuesta_original=None, credentials=None) -> JsonResponse:
    """Lo que se responde mientras una cuenta está bloqueada por intentos fallidos (RNF-ACC-07).

    La invoca django-axes en lugar de su página propia, para que el mensaje
    sea el nuestro y no revele nada del sistema.
    """
    return _rechazo(MENSAJE_DE_BLOQUEO, status=429)


def _rechazo(mensaje: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"mensaje": mensaje}, status=status)


def _leer_textos(request: HttpRequest, *campos: str) -> tuple[str, ...] | None:
    """Extrae del cuerpo JSON los campos pedidos. Devuelve None si falta alguno o no es texto."""
    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(datos, dict):
        return None

    valores = tuple(datos.get(campo) for campo in campos)
    if not all(isinstance(valor, str) for valor in valores):
        return None
    return valores


def _datos_de(cuenta) -> dict[str, str | bool]:
    """Lo único de una cuenta que sale del servidor. Nunca la contraseña."""
    return {
        "usuario": cuenta.usuario,
        "correo": cuenta.correo,
        "nombre": cuenta.nombre,
        "debe_cambiar_contrasena": cuenta.debe_cambiar_contrasena,
    }
