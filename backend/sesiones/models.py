"""Sesiones de entrenamiento: lo que de verdad se hizo (spec 006, plan 4.2).

Tres decisiones de diseño que explican la forma de estas tablas:

- Los identificadores son UUID generados en el celular: una serie creada sin
  señal ya nace con su identidad definitiva y reenviarla no la duplica.
- El nombre del ejercicio y su grupo se guardan como copia, no como
  referencia: modificar o eliminar una rutina no toca el historial (RF-006-11).
- Los rangos también se vigilan en la base, por si algún código se salta las reglas.
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from reglas import ejercicios as reglas_de_ejercicios
from reglas import series as reglas_de_series
from reglas import textos as reglas_de_textos


class Sesion(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sesiones")
    nombre = models.CharField(max_length=reglas_de_textos.LARGO_MAXIMO_NOMBRE)
    inicio = models.DateTimeField()
    fin = models.DateTimeField(null=True, blank=True)
    nota = models.CharField(max_length=reglas_de_textos.LARGO_MAXIMO_NOTA, blank=True)
    # Verdadero si la cerró el servidor a las 2 horas y el celular aún no ha
    # enviado su propio cierre (que, cuando llegue, lo reemplaza).
    cierre_automatico = models.BooleanField(default=False)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "sesión"
        verbose_name_plural = "sesiones"
        constraints = [
            # RF-006-02: como máximo una sesión en curso por persona.
            models.UniqueConstraint(
                fields=["usuario"], condition=Q(fin__isnull=True), name="sesiones_una_en_curso_por_usuario"
            ),
            models.CheckConstraint(
                condition=Q(fin__isnull=True) | Q(fin__gte=F("inicio")), name="sesiones_fin_no_antes_del_inicio"
            ),
        ]
        indexes = [models.Index(fields=["usuario", "-fin"], name="sesiones_historial")]

    def __str__(self) -> str:
        return f"{self.nombre} ({self.inicio:%Y-%m-%d})"


class SesionEjercicio(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="ejercicios")
    nombre = models.CharField(max_length=reglas_de_ejercicios.LARGO_MAXIMO_NOMBRE_DE_EJERCICIO)
    # Forma canónica del nombre, para reconocer el mismo ejercicio escrito distinto (RN-006-08).
    clave = models.CharField(max_length=reglas_de_ejercicios.LARGO_MAXIMO_NOMBRE_DE_EJERCICIO, db_index=True)
    grupo = models.CharField(max_length=reglas_de_ejercicios.LARGO_MAXIMO_GRUPO)
    orden = models.PositiveSmallIntegerField()
    nota = models.CharField(max_length=reglas_de_textos.LARGO_MAXIMO_NOTA, blank=True)

    class Meta:
        verbose_name = "ejercicio de una sesión"
        verbose_name_plural = "ejercicios de una sesión"
        ordering = ["orden", "nombre"]

    def __str__(self) -> str:
        return self.nombre


class Serie(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    ejercicio = models.ForeignKey(SesionEjercicio, on_delete=models.CASCADE, related_name="series")
    numero = models.PositiveSmallIntegerField()
    peso = models.DecimalField(max_digits=4, decimal_places=1)
    reps = models.PositiveSmallIntegerField()
    confirmada = models.BooleanField(default=False)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "serie"
        verbose_name_plural = "series"
        ordering = ["numero"]
        constraints = [
            models.UniqueConstraint(fields=["ejercicio", "numero"], name="series_numero_unico_por_ejercicio"),
            models.CheckConstraint(
                condition=Q(peso__gte=reglas_de_series.PESO_MINIMO) & Q(peso__lte=reglas_de_series.PESO_MAXIMO),
                name="series_peso_en_rango",
            ),
            models.CheckConstraint(
                condition=Q(reps__gte=reglas_de_series.REPETICIONES_MINIMAS)
                & Q(reps__lte=reglas_de_series.REPETICIONES_MAXIMAS),
                name="series_reps_en_rango",
            ),
            models.CheckConstraint(
                condition=Q(numero__gte=reglas_de_ejercicios.SERIES_MINIMAS)
                & Q(numero__lte=reglas_de_ejercicios.SERIES_MAXIMAS),
                name="series_numero_en_rango",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.numero}: {self.peso} kg x {self.reps}"
