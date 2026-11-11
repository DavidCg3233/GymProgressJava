"""Reglas del cuerpo: peso, estatura, fecha, IMC y peso objetivo (spec 003, plan 003).

Todo con Decimal: 99,9 ÷ 2,00² da exactamente 24,975 y no 24,974999.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .errores import ErrorDeValidacion

# RN-003-03.
PESO_MINIMO = Decimal("20.0")
PESO_MAXIMO = Decimal("300.0")
UN_DECIMAL = Decimal("0.1")

# RN-003-04: en centímetros.
ESTATURA_MINIMA = 100
ESTATURA_MAXIMA = 250

# RN-003-02 (OMS): límite inferior de cada categoría.
CATEGORIAS = [
    (Decimal("30"), "Obesidad"),
    (Decimal("25"), "Sobrepeso"),
    (Decimal("18.5"), "Normal"),
]

_MENSAJE_PESO = "El peso va de 20 a 300 kg, con un decimal."
_MENSAJE_ESTATURA = f"La estatura va en centímetros, de {ESTATURA_MINIMA} a {ESTATURA_MAXIMA}."


def validar_peso_corporal(valor: object) -> Decimal:
    """RN-003-03: de 20,0 a 300,0 kg, con un decimal como máximo."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ErrorDeValidacion("peso", "Escribe tu peso.")
    peso = _a_decimal(valor)
    if peso is None or not PESO_MINIMO <= peso <= PESO_MAXIMO or peso % UN_DECIMAL != 0:
        raise ErrorDeValidacion("peso", _MENSAJE_PESO)
    return peso


def validar_estatura(valor: object) -> int:
    """RN-003-04: entero de 100 a 250 cm. 1,75 se rechaza: va en centímetros."""
    if isinstance(valor, bool) or not isinstance(valor, int) or not ESTATURA_MINIMA <= valor <= ESTATURA_MAXIMA:
        raise ErrorDeValidacion("estatura", _MENSAJE_ESTATURA)
    return valor


def validar_fecha_de_peso(valor: object, hoy: date) -> date:
    """RN-003-05: obligatoria, como "AAAA-MM-DD", y no futura."""
    if isinstance(valor, date):
        fecha = valor
    else:
        try:
            fecha = date.fromisoformat(valor) if isinstance(valor, str) and len(valor) == 10 else None
        except ValueError:
            fecha = None
    if fecha is None:
        raise ErrorDeValidacion("fecha", "Escribe una fecha válida.")
    if fecha > hoy:
        raise ErrorDeValidacion("fecha", "La fecha no puede ser futura.")
    return fecha


def imc(peso: Decimal, estatura_cm: int) -> Decimal:
    """RN-003-01: peso ÷ estatura en metros al cuadrado, sin redondear."""
    metros = Decimal(estatura_cm) / 100
    return peso / (metros * metros)


def imc_para_mostrar(valor: Decimal) -> Decimal:
    """RN-003-01: un decimal. La mitad sube (plan 003, regla nueva 2)."""
    return valor.quantize(UN_DECIMAL, rounding=ROUND_HALF_UP)


def categoria_de_imc(valor: Decimal) -> str:
    """RN-003-02: se decide con el IMC exacto, nunca con el redondeado."""
    for limite, nombre in CATEGORIAS:
        if valor >= limite:
            return nombre
    return "Bajo peso"


def cambio(anterior: Decimal, actual: Decimal) -> tuple[Decimal, str]:
    """RF-003-04: cuánto cambió frente al registro anterior y hacia dónde."""
    diferencia = actual - anterior
    direccion = "subio" if diferencia > 0 else "bajo" if diferencia < 0 else "igual"
    return abs(diferencia), direccion


def hacia_el_objetivo(primero: Decimal, actual: Decimal, objetivo: Decimal) -> dict:
    """RN-003-08: la dirección sale del primer registro.

    Plan 003, regla nueva 1: si el objetivo es igual al primer registro, es
    "mantener"; se alcanza solo con el peso exacto y, si te alejas, la
    dirección la marca el peso actual.
    """
    if objetivo < primero:
        direccion, alcanzado = "bajar", actual <= objetivo
    elif objetivo > primero:
        direccion, alcanzado = "subir", actual >= objetivo
    else:
        alcanzado = actual == objetivo
        direccion = "mantener" if alcanzado else "bajar" if actual > objetivo else "subir"
    return {"faltan": Decimal(0) if alcanzado else abs(actual - objetivo), "direccion": direccion, "alcanzado": alcanzado}


def _a_decimal(valor: object) -> Decimal | None:
    """Se pasa por texto para no heredar la imprecisión de la coma flotante."""
    if isinstance(valor, bool):
        return None
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        return None
    return numero if numero.is_finite() else None
