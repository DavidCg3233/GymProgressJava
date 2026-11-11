"""Peso corporal (spec 003, plan 003 sección 4.1).

Un registro por usuario y por día: la fecha es su dirección en la API.
La base defiende las reglas por sí sola, aunque algún código se las salte.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class RegistroDePeso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pesos")
    fecha = models.DateField()
    peso = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        verbose_name = "registro de peso"
        verbose_name_plural = "registros de peso"
        ordering = ["-fecha"]
        constraints = [
            # RN-003-06: uno por día.
            models.UniqueConstraint(fields=["usuario", "fecha"], name="cuerpo_un_registro_por_dia"),
            # RN-003-03.
            models.CheckConstraint(
                condition=models.Q(peso__gte=Decimal("20.0"), peso__lte=Decimal("300.0")),
                name="cuerpo_peso_de_20_a_300",
            ),
        ]

    def __str__(self) -> str:
        # Sin el peso: es un dato de salud (plan 003, sección 7).
        return f"Registro del {self.fecha.isoformat()}"
