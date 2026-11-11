"""Crea la cuenta del dueño al arrancar, si todavía no existe (RNF-ACC-05, RNF-ACC-09).

Lee GP_DUENO_USUARIO, GP_DUENO_CORREO, GP_DUENO_NOMBRE y
GP_DUENO_CONTRASENA_TEMPORAL. La contraseña queda marcada como temporal: la
app obliga a cambiarla al entrar. Después de entrar, esas variables se pueden
borrar de Railway; si ya hay un dueño, el comando no hace nada.

Nunca escribe la contraseña en los registros (RNF-SEG-08) y nunca falla: un
problema aquí no debe impedir que la app arranque.
"""

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from cuentas.models import LimiteDeCuentasAlcanzado

VARIABLES = ("GP_DUENO_USUARIO", "GP_DUENO_CORREO", "GP_DUENO_NOMBRE", "GP_DUENO_CONTRASENA_TEMPORAL")


class Command(BaseCommand):
    help = "Crea la cuenta del dueño a partir de variables de entorno, si aún no existe."

    def handle(self, *args, **opciones):
        Usuario = get_user_model()
        if Usuario.objects.filter(is_superuser=True).exists():
            self.stdout.write("Cuenta de dueño: ya existe, no se hizo nada.")
            return

        valores = {nombre: os.environ.get(nombre, "").strip() for nombre in VARIABLES}
        faltan = [nombre for nombre, valor in valores.items() if not valor]
        if faltan:
            self.stdout.write(f"Cuenta de dueño: no se creó. Faltan las variables {', '.join(faltan)}.")
            return

        usuario, correo, nombre, temporal = valores.values()
        candidata = Usuario(usuario=usuario, correo=correo, nombre=nombre)
        try:
            validate_password(temporal, user=candidata)
        except ValidationError as error:
            # Los mensajes de Django describen la regla, no repiten la contraseña.
            self.stdout.write(f"Cuenta de dueño: no se creó. La contraseña temporal no sirve: {' '.join(error.messages)}")
            return

        try:
            Usuario.objects.create_superuser(
                usuario=usuario, correo=correo, nombre=nombre, password=temporal, debe_cambiar_contrasena=True
            )
        except LimiteDeCuentasAlcanzado as error:
            self.stdout.write(f"Cuenta de dueño: no se creó. {error}")
            return
        self.stdout.write(f"Cuenta de dueño creada: {usuario}. Al entrar, la app pedirá cambiar la contraseña.")
