"""Reglas de progreso: récords, volumen, semanas, meta y grupos (spec 004, plan 004).

Funciones puras: reciben datos ya filtrados (solo series confirmadas de
sesiones terminadas, RN-004-01) y no saben nada de la base de datos.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from .ejercicios import clave_de_ejercicio
from .errores import ErrorDeValidacion

# RF-004-05: la semana actual y las 11 anteriores.
SEMANAS_DE_HISTORIA = 12

# RN-004-08.
META_MINIMA = 1
META_MAXIMA = 14


@dataclass(frozen=True)
class SerieHecha:
    """Una serie confirmada. `cuando` ordena de la más antigua a la más nueva."""

    peso: Decimal
    reps: int
    cuando: Any = 0


def es_de_peso_corporal(series: list[SerieHecha]) -> bool:
    """RN-004-04: todas las series del ejercicio pesan 0."""
    return bool(series) and all(serie.peso == 0 for serie in series)


def mejor_serie(series: Iterable[SerieHecha]) -> SerieHecha | None:
    """Récord (RN-004-03) y serie más pesada de una sesión (RN-004-05).

    Gana el mayor peso; con el mismo peso, más repeticiones; si siguen
    empatadas, la más antigua. En peso corporal todas pesan 0, así que gana
    la de más repeticiones (RN-004-04).
    """
    # Se ordena primero por antigüedad para que, en un empate, `max` se quede con la primera.
    return max(sorted(series, key=lambda serie: serie.cuando), key=lambda serie: (serie.peso, serie.reps), default=None)


def volumen(series: Iterable[SerieHecha], peso_corporal: bool) -> Decimal | int:
    """RN-004-06: suma de peso × reps; en peso corporal, suma de reps."""
    if peso_corporal:
        return sum(serie.reps for serie in series)
    return sum((serie.peso * serie.reps for serie in series), Decimal(0))


def inicio_de_semana(dia: date) -> date:
    """RN-004-02: la semana va de lunes a domingo."""
    return dia - timedelta(days=dia.weekday())


def sesiones_por_semana(fechas: Iterable[date], hoy: date) -> list[tuple[date, int]]:
    """RN-004-07: sesiones por semana, de la más antigua a la actual, con 0 en las vacías.

    `fechas` es el día local en que empezó cada sesión terminada.
    """
    actual = inicio_de_semana(hoy)
    semanas = {actual - timedelta(weeks=atras): 0 for atras in range(SEMANAS_DE_HISTORIA - 1, -1, -1)}
    for fecha in fechas:
        lunes = inicio_de_semana(fecha)
        if lunes in semanas:
            semanas[lunes] += 1
    return list(semanas.items())


def cumple(sesiones: int, meta: int | None) -> bool | None:
    """RN-004-08: una semana cumple si llegó a la meta. Sin meta no se juzga."""
    if meta is None:
        return None
    return sesiones >= meta


def validar_meta(valor: object) -> int | None:
    """RN-004-08: entero de 1 a 14, o None para no tener meta."""
    if valor is None:
        return None
    if isinstance(valor, bool) or not isinstance(valor, int) or not META_MINIMA <= valor <= META_MAXIMA:
        raise ErrorDeValidacion("meta", f"La meta va de {META_MINIMA} a {META_MAXIMA} sesiones por semana.")
    return valor


def ordenar_grupos(conteos: dict[str, int]) -> list[tuple[str, int]]:
    """RN-004-09: de más series a menos. Empates por nombre (plan 004, regla nueva 1)."""
    return sorted(conteos.items(), key=lambda grupo: (-grupo[1], clave_de_ejercicio(grupo[0])))
