"""Cómo se comprueba la identidad de quien entra (RNF-ACC-01)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import normalizar_identificador


def buscar_cuenta(identificador: str):
    """La cuenta cuyo usuario o correo coincide con el identificador ya normalizado."""
    if not identificador:
        return None
    return get_user_model().objects.filter(Q(usuario=identificador) | Q(correo=identificador)).first()


def clave_de_bloqueo(request, credentials=None) -> str:
    """A nombre de quién se cuentan los intentos fallidos (RNF-ACC-07).

    Los fallos se suman a la cuenta, sin importar si se escribió el usuario o
    el correo, ni con qué mayúsculas: así el límite no se evade cambiando la
    forma de escribir. Si la cuenta no existe, se cuenta por lo que se
    escribió, para que el bloqueo no revele qué cuentas existen.
    """
    escrito = (credentials or {}).get("username") or getattr(request, "identificador_de_acceso", "")
    identificador = normalizar_identificador(escrito)
    cuenta = buscar_cuenta(identificador)
    return cuenta.usuario if cuenta else identificador


class UsuarioOCorreo(ModelBackend):
    """Permite entrar con el nombre de usuario o con el correo, indistintamente."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identificador = normalizar_identificador(username)
        Usuario = get_user_model()

        if not identificador or not password:
            return None

        cuenta = buscar_cuenta(identificador)
        if cuenta is None:
            # Se cifra igual una contraseña, para que responder tarde lo mismo
            # exista o no la cuenta y no se pueda averiguar cuáles existen.
            Usuario().set_password(password)
            return None

        if cuenta.check_password(password) and self.user_can_authenticate(cuenta):
            return cuenta
        return None
