"""Cuentas de GymProgress.

De cada persona se guarda lo mínimo (RNF-ACC-10): nombre para mostrar, nombre
de usuario, correo y contraseña. La contraseña la cifra Django con Argon2 y
nunca queda legible (RNF-SEG-01).
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower


def normalizar_identificador(valor: str | None) -> str:
    """Usuario y correo se comparan sin distinguir mayúsculas ni espacios sobrantes."""
    return (valor or "").strip().lower()


class GestorDeUsuarios(BaseUserManager):
    """Única puerta para crear cuentas: valida lo obligatorio y cifra la contraseña."""

    def create_user(self, usuario: str, correo: str, nombre: str, password: str | None = None, **extra):
        cuenta = self.model(
            usuario=self._exigir("usuario", normalizar_identificador(usuario)),
            correo=self._exigir("correo", normalizar_identificador(correo)),
            nombre=self._exigir("nombre", (nombre or "").strip()),
            **extra,
        )
        cuenta.set_password(password)
        cuenta.save(using=self._db)
        return cuenta

    def create_superuser(self, usuario: str, correo: str, nombre: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(usuario, correo, nombre, password, **extra)

    @staticmethod
    def _exigir(campo: str, valor: str) -> str:
        if not valor:
            raise ValueError(f"El campo {campo} es obligatorio.")
        return valor


class Usuario(AbstractBaseUser, PermissionsMixin):
    usuario = models.CharField("nombre de usuario", max_length=30, unique=True)
    correo = models.EmailField("correo", unique=True)
    nombre = models.CharField("nombre para mostrar", max_length=50)

    is_active = models.BooleanField("activa", default=True)
    is_staff = models.BooleanField("puede entrar al panel de administración", default=False)
    creada = models.DateTimeField("creada", auto_now_add=True)

    objects = GestorDeUsuarios()

    USERNAME_FIELD = "usuario"
    EMAIL_FIELD = "correo"
    REQUIRED_FIELDS = ["correo", "nombre"]

    class Meta:
        verbose_name = "cuenta"
        verbose_name_plural = "cuentas"
        constraints = [
            # La base rechaza duplicados que solo difieren en mayúsculas,
            # aunque algún código se salte el normalizado de `save`.
            models.UniqueConstraint(Lower("usuario"), name="cuentas_usuario_unico_sin_mayusculas"),
            models.UniqueConstraint(Lower("correo"), name="cuentas_correo_unico_sin_mayusculas"),
        ]

    def __str__(self) -> str:
        return self.usuario

    def save(self, *args, **kwargs):
        self.usuario = normalizar_identificador(self.usuario)
        self.correo = normalizar_identificador(self.correo)
        self.nombre = (self.nombre or "").strip()
        super().save(*args, **kwargs)
