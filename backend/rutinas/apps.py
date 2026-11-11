from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save


class RutinasConfig(AppConfig):
    name = "rutinas"
    verbose_name = "Rutinas y catálogo"

    def ready(self):
        # RF-002-14: cada cuenta nueva arranca con el catálogo predefinido.
        # Se hace con una señal para que `cuentas` no dependa de `rutinas`.
        post_save.connect(cargar_catalogo_al_crear_cuenta, sender=settings.AUTH_USER_MODEL)


def cargar_catalogo_al_crear_cuenta(sender, instance, created, raw=False, **kwargs):
    if not created or raw:
        return
    from . import catalogo_inicial
    from .models import Ejercicio, GrupoMuscular

    catalogo_inicial.cargar(instance, GrupoMuscular, Ejercicio)
