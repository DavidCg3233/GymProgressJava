"""Reglas de una serie: peso y repeticiones (spec 006, RF-006-24)."""

from decimal import Decimal, InvalidOperation

from .errores import ErrorDeValidacion

# RN-006-02 y RN-006-03: de 0 a 500 kg en múltiplos de 0,5; 0 es peso corporal.
PESO_MINIMO = Decimal("0")
PESO_MAXIMO = Decimal("500")
PASO_DE_PESO = Decimal("0.5")

# RN-006-04: entero de 1 a 100.
REPETICIONES_MINIMAS = 1
REPETICIONES_MAXIMAS = 100

_CAMPO_PESO = "peso"
_CAMPO_REPS = "reps"


def validar_peso(valor: object) -> Decimal:
    """Devuelve el peso como decimal exacto, o explica por qué no es válido."""
    if _esta_vacio(valor):
        raise ErrorDeValidacion(_CAMPO_PESO, "Escribe el peso.")

    peso = _a_decimal(valor)
    if peso is None:
        raise ErrorDeValidacion(_CAMPO_PESO, "El peso debe ser un número.")
    if not PESO_MINIMO <= peso <= PESO_MAXIMO:
        raise ErrorDeValidacion(_CAMPO_PESO, "El peso debe estar entre 0 y 500 kg.")
    if peso % PASO_DE_PESO != 0:
        raise ErrorDeValidacion(_CAMPO_PESO, "El peso va de a 0,5 kg.")
    return peso


def validar_repeticiones(valor: object) -> int:
    """Devuelve las repeticiones como entero, o explica por qué no son válidas."""
    if _esta_vacio(valor):
        raise ErrorDeValidacion(_CAMPO_REPS, "Escribe las repeticiones.")

    cantidad = _a_decimal(valor)
    if cantidad is None or cantidad != cantidad.to_integral_value():
        raise ErrorDeValidacion(_CAMPO_REPS, "Las repeticiones deben ser un número entero.")
    if not REPETICIONES_MINIMAS <= cantidad <= REPETICIONES_MAXIMAS:
        raise ErrorDeValidacion(_CAMPO_REPS, "Las repeticiones deben estar entre 1 y 100.")
    return int(cantidad)


def _esta_vacio(valor: object) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _a_decimal(valor: object) -> Decimal | None:
    """Convierte a decimal exacto. Devuelve None si no es un número finito.

    Se pasa por texto para no heredar la imprecisión de la coma flotante:
    Decimal(30.3) no es 30,3, pero Decimal("30.3") sí.
    """
    if isinstance(valor, bool):
        return None
    texto = str(valor).strip().replace(",", ".")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    return numero if numero.is_finite() else None
