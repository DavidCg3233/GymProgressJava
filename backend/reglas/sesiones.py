"""Reglas del ciclo de vida de una sesión de entrenamiento (spec 006)."""

from datetime import datetime, timedelta

# RN-006-06: una sesión en curso dura como máximo 2 horas desde su inicio.
DURACION_MAXIMA = timedelta(hours=2)


def hora_de_cierre_automatico(inicio: datetime) -> datetime:
    """Momento en que una sesión olvidada se da por terminada (RN-006-12)."""
    _exigir_zona_horaria(inicio)
    return inicio + DURACION_MAXIMA


def debe_cerrarse(inicio: datetime, ahora: datetime) -> bool:
    """Indica si una sesión en curso ya cumplió su duración máxima (RF-006-08)."""
    _exigir_zona_horaria(ahora)
    return ahora >= hora_de_cierre_automatico(inicio)


def debe_descartarse(series_confirmadas: int) -> bool:
    """Una sesión que termina sin series confirmadas no se guarda (RF-006-19)."""
    if series_confirmadas < 0:
        raise ValueError("La cantidad de series confirmadas no puede ser negativa.")
    return series_confirmadas == 0


def _exigir_zona_horaria(momento: datetime) -> None:
    if momento.tzinfo is None or momento.utcoffset() is None:
        raise ValueError("La hora debe incluir su zona horaria.")
