"""Entrar, salir y consultar el estado del acceso (T-006-10)."""

import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

# Un solo mensaje para todo rechazo: no revela si falló el usuario, la
# contraseña o si la cuenta está desactivada (RNF-SEG-09).
MENSAJE_DE_RECHAZO = "Usuario o contraseña incorrectos."


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
    identificador, contrasena = _leer_credenciales(request)
    cuenta = authenticate(request, username=identificador, password=contrasena)
    if cuenta is None:
        return JsonResponse({"mensaje": MENSAJE_DE_RECHAZO}, status=400)

    # `login` estrena identificador de sesión: nadie puede fijarlo de antemano.
    login(request, cuenta)
    return JsonResponse({"cuenta": _datos_de(cuenta)})


@require_POST
def salir(request: HttpRequest) -> HttpResponse:
    """Borra la sesión en el servidor: la cookie anterior deja de servir (RNF-ACC-04)."""
    logout(request)
    return HttpResponse(status=204)


def _leer_credenciales(request: HttpRequest) -> tuple[str, str]:
    """Extrae identificador y contraseña. Cualquier cuerpo inesperado equivale a vacío."""
    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return "", ""
    if not isinstance(datos, dict):
        return "", ""

    identificador = datos.get("identificador")
    contrasena = datos.get("contrasena")
    if not isinstance(identificador, str) or not isinstance(contrasena, str):
        return "", ""
    return identificador, contrasena


def _datos_de(cuenta) -> dict[str, str]:
    """Lo único de una cuenta que sale del servidor. Nunca la contraseña."""
    return {"usuario": cuenta.usuario, "correo": cuenta.correo, "nombre": cuenta.nombre}
