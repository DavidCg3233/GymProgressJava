"""Migración de datos de la versión con rutinas (T-002-05, plan 002 sección 4.3).

Para cada cuenta que ya existía:
1. Carga el catálogo predefinido (las cuentas nuevas lo reciben al crearse).
2. Enlaza cada ejercicio de sus sesiones con el ejercicio del catálogo de igual
   nombre; si no existe, lo crea con el grupo que traía la sesión.

Se puede aplicar varias veces: lo que ya está no se toca.
"""

from django.conf import settings

from . import catalogo_inicial


def aplicar(apps, schema_editor=None) -> None:
    Usuario = apps.get_model(settings.AUTH_USER_MODEL)
    GrupoMuscular = apps.get_model("rutinas", "GrupoMuscular")
    Ejercicio = apps.get_model("rutinas", "Ejercicio")
    SesionEjercicio = apps.get_model("sesiones", "SesionEjercicio")

    for usuario in Usuario.objects.all():
        catalogo_inicial.cargar(usuario, GrupoMuscular, Ejercicio)

        sin_enlace = SesionEjercicio.objects.filter(sesion__usuario=usuario, ejercicio__isnull=True)
        for hecho in sin_enlace:
            hecho.ejercicio = catalogo_inicial.asegurar_ejercicio(
                usuario, hecho.nombre, hecho.grupo, GrupoMuscular, Ejercicio
            )
            hecho.save(update_fields=["ejercicio"])
