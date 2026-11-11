"""Catálogo de ejercicios y rutinas de cada persona (spec 002, plan 002 sección 4.1).

- Todo es propio de cada usuario: renombrar o borrar algo nunca toca a otro (RF-002-10).
- `clave` es el nombre sin mayúsculas, tildes ni espacios repetidos. La unicidad
  se mide sobre ella: "Press Banca" y "press banca" son el mismo (RN-002-07).
- Los rangos también se vigilan en la base, por si algún código se salta las reglas.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q

from reglas import ejercicios as reglas_de_ejercicios
from reglas import rutinas as reglas_de_rutinas
from reglas import series as reglas_de_series


class ConClave(models.Model):
    """Nombre visible más su forma canónica para comparar."""

    nombre = models.CharField(max_length=50)
    clave = models.CharField(max_length=50, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.nombre = (self.nombre or "").strip()
        self.clave = reglas_de_ejercicios.clave_de_ejercicio(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nombre


class GrupoMuscular(ConClave):
    id = models.UUIDField(primary_key=True, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grupos")
    nombre = models.CharField(max_length=reglas_de_ejercicios.LARGO_MAXIMO_GRUPO)

    class Meta:
        verbose_name = "grupo muscular"
        verbose_name_plural = "grupos musculares"
        ordering = ["nombre"]
        constraints = [models.UniqueConstraint(fields=["usuario", "clave"], name="rutinas_grupo_unico_por_usuario")]


class Ejercicio(ConClave):
    id = models.UUIDField(primary_key=True, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ejercicios")
    nombre = models.CharField(max_length=reglas_de_ejercicios.LARGO_MAXIMO_NOMBRE_DE_EJERCICIO)
    # RF-002-19: un grupo con ejercicios no se puede borrar. RESTRICT y no PROTECT:
    # PROTECT también impediría eliminar la cuenta completa, aunque sus ejercicios
    # se borren en la misma operación.
    grupo = models.ForeignKey(GrupoMuscular, on_delete=models.RESTRICT, related_name="ejercicios")

    class Meta:
        verbose_name = "ejercicio"
        verbose_name_plural = "ejercicios"
        ordering = ["nombre"]
        constraints = [models.UniqueConstraint(fields=["usuario", "clave"], name="rutinas_ejercicio_unico_por_usuario")]


class Rutina(ConClave):
    id = models.UUIDField(primary_key=True, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rutinas")
    nombre = models.CharField(max_length=reglas_de_rutinas.LARGO_MAXIMO_NOMBRE_DE_RUTINA)
    # RN-002-02: cada bit es un día, de lunes (1) a domingo (64). 0 = sin día.
    dias = models.PositiveSmallIntegerField(default=0)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "rutina"
        verbose_name_plural = "rutinas"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["usuario", "clave"], name="rutinas_rutina_unica_por_usuario"),
            models.CheckConstraint(condition=Q(dias__gte=0) & Q(dias__lte=127), name="rutinas_dias_en_rango"),
        ]


class RutinaEjercicio(models.Model):
    """Un ejercicio previsto en una rutina. Sus series comparten reps y peso (RN-002-09)."""

    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name="ejercicios")
    # RF-002-16: borrar un ejercicio del catálogo lo quita de las rutinas.
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name="en_rutinas")
    orden = models.PositiveSmallIntegerField()
    series = models.PositiveSmallIntegerField()
    reps = models.PositiveSmallIntegerField()
    peso = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        verbose_name = "ejercicio de una rutina"
        verbose_name_plural = "ejercicios de una rutina"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(fields=["rutina", "ejercicio"], name="rutinas_ejercicio_una_vez_por_rutina"),
            models.CheckConstraint(
                condition=Q(series__gte=reglas_de_rutinas.SERIES_PREVISTAS_MINIMAS)
                & Q(series__lte=reglas_de_rutinas.SERIES_PREVISTAS_MAXIMAS),
                name="rutinas_series_en_rango",
            ),
            models.CheckConstraint(
                condition=Q(reps__gte=reglas_de_series.REPETICIONES_MINIMAS)
                & Q(reps__lte=reglas_de_series.REPETICIONES_MAXIMAS),
                name="rutinas_reps_en_rango",
            ),
            models.CheckConstraint(
                condition=Q(peso__gte=reglas_de_series.PESO_MINIMO) & Q(peso__lte=reglas_de_series.PESO_MAXIMO),
                name="rutinas_peso_en_rango",
            ),
        ]
