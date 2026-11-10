"""Base común de la API: quién puede entrar y cómo se responden los errores (T-006-13).

Toda vista de la API hereda estas reglas desde la configuración, así que una
vista nueva queda protegida aunque quien la escriba no haga nada especial.
"""

from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from reglas.errores import ErrorDeValidacion
from sesiones.servicios import Conflicto, NoEncontrado

MENSAJE_SIN_ACCESO = "Entra con tu cuenta para continuar."
MENSAJE_CONTRASENA_TEMPORAL = "Cambia tu contraseña temporal para continuar."
MENSAJE_NO_ENCONTRADO = "No encontramos lo que buscas."
MENSAJE_PETICION_INVALIDA = "No pudimos entender la petición."
MENSAJE_NO_PERMITIDO = "No se pudo comprobar la petición. Recarga la página e inténtalo de nuevo."
MENSAJE_ERROR_INTERNO = "Algo salió mal de nuestro lado. Inténtalo de nuevo."


class AccesoPorSesion(SessionAuthentication):
    """El acceso es la cookie de sesión de Django, con su protección CSRF (RNF-ACC-02)."""

    def authenticate_header(self, request) -> str:
        # Con esta cabecera, quien no ha entrado recibe 401 en lugar de 403.
        return "Session"


class AccesoVigente(BasePermission):
    """Exige haber entrado y no estar usando una contraseña temporal (RNF-ACC-09)."""

    message = MENSAJE_CONTRASENA_TEMPORAL

    def has_permission(self, request, view) -> bool:
        cuenta = request.user
        return bool(cuenta and cuenta.is_authenticated and not cuenta.debe_cambiar_contrasena)


def responder_error(error: Exception, contexto) -> Response:
    """Convierte cualquier error en un mensaje para el usuario, sin detalles internos (RNF-SEG-09)."""
    if isinstance(error, ErrorDeValidacion):
        return _respuesta(status.HTTP_400_BAD_REQUEST, error.mensaje, campo=error.campo)
    if isinstance(error, Conflicto):
        return _respuesta(status.HTTP_409_CONFLICT, error.mensaje, **error.extra)
    if isinstance(error, (NoEncontrado, Http404, exceptions.NotFound)):
        return _respuesta(status.HTTP_404_NOT_FOUND, MENSAJE_NO_ENCONTRADO)
    if isinstance(error, exceptions.NotAuthenticated):
        return _respuesta(status.HTTP_401_UNAUTHORIZED, MENSAJE_SIN_ACCESO)
    if isinstance(error, exceptions.PermissionDenied):
        es_la_nuestra = str(error.detail) == MENSAJE_CONTRASENA_TEMPORAL
        return _respuesta(status.HTTP_403_FORBIDDEN, MENSAJE_CONTRASENA_TEMPORAL if es_la_nuestra else MENSAJE_NO_PERMITIDO)
    if isinstance(error, exceptions.APIException) and error.status_code < 500:
        return _respuesta(error.status_code, MENSAJE_PETICION_INVALIDA)
    # Cualquier otro error es nuestro: Django lo registra y el usuario no ve el detalle.
    return None


def _respuesta(codigo: int, mensaje: str, **extra) -> Response:
    return Response({"mensaje": mensaje, **extra}, status=codigo)
