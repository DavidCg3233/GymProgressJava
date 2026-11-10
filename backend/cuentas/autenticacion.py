"""Cómo se comprueba la identidad de quien entra (RNF-ACC-01)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import normalizar_identificador


class UsuarioOCorreo(ModelBackend):
    """Permite entrar con el nombre de usuario o con el correo, indistintamente."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identificador = normalizar_identificador(username)
        Usuario = get_user_model()

        if not identificador or not password:
            return None

        cuenta = Usuario.objects.filter(Q(usuario=identificador) | Q(correo=identificador)).first()
        if cuenta is None:
            # Se cifra igual una contraseña, para que responder tarde lo mismo
            # exista o no la cuenta y no se pueda averiguar cuáles existen.
            Usuario().set_password(password)
            return None

        if cuenta.check_password(password) and self.user_can_authenticate(cuenta):
            return cuenta
        return None
