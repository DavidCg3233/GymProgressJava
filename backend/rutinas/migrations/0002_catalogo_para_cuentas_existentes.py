"""Carga el catálogo predefinido a las cuentas que ya existían y enlaza sus sesiones (T-002-05).

La lógica vive en `rutinas/migracion_de_datos.py`, donde tiene sus pruebas.
Deshacer esta migración no borra nada: el catálogo cargado se queda.
"""

from django.db import migrations

from rutinas.migracion_de_datos import aplicar


class Migration(migrations.Migration):
    dependencies = [
        ("rutinas", "0001_initial"),
        ("sesiones", "0002_sesion_rutina_sesionejercicio_ejercicio"),
    ]

    operations = [migrations.RunPython(aplicar, migrations.RunPython.noop)]
