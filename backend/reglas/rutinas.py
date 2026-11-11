"""Reglas de una rutina (spec 002, plan 002)."""

from .ejercicios import clave_de_ejercicio
from .errores import ErrorDeValidacion
from .textos import exigir_texto

# RN-002-01.
LARGO_MAXIMO_NOMBRE_DE_RUTINA = 50

# RN-002-03.
MAXIMO_DE_EJERCICIOS = 20

# RN-002-04.
SERIES_PREVISTAS_MINIMAS = 1
SERIES_PREVISTAS_MAXIMAS = 10

# RN-002-02: 1 = lunes ... 7 = domingo.
DIAS_DE_LA_SEMANA = range(1, 8)

_MENSAJE_DIAS = "Los días van de lunes (1) a domingo (7), sin repetir."


def validar_nombre_de_rutina(valor: object) -> str:
    nombre = exigir_texto(valor, "nombre").strip()
    if not nombre:
        raise ErrorDeValidacion("nombre", "Escribe el nombre de la rutina.")
    if len(nombre) > LARGO_MAXIMO_NOMBRE_DE_RUTINA:
        raise ErrorDeValidacion(
            "nombre", f"El nombre de la rutina admite máximo {LARGO_MAXIMO_NOMBRE_DE_RUTINA} caracteres."
        )
    return nombre


def validar_dias(valor: object) -> list[int]:
    """Devuelve los días ordenados. Una lista vacía es válida: la rutina no tiene día."""
    if not isinstance(valor, list):
        raise ErrorDeValidacion("dias", _MENSAJE_DIAS)
    validos = all(isinstance(dia, int) and not isinstance(dia, bool) and dia in DIAS_DE_LA_SEMANA for dia in valor)
    if not validos or len(set(valor)) != len(valor):
        raise ErrorDeValidacion("dias", _MENSAJE_DIAS)
    return sorted(valor)


def dias_a_bits(dias: list[int]) -> int:
    """Cada día es un bit: lunes = 1, martes = 2, miércoles = 4 ... domingo = 64."""
    return sum(1 << (dia - 1) for dia in dias)


def bits_a_dias(bits: int) -> list[int]:
    return [dia for dia in DIAS_DE_LA_SEMANA if tiene_dia(bits, dia)]


def tiene_dia(bits: int, dia: int) -> bool:
    return bool(bits & (1 << (dia - 1)))


def validar_ejercicios_de_rutina(claves: list[str]) -> None:
    """Recibe las claves de los ejercicios de la rutina, en orden."""
    if not claves:
        raise ErrorDeValidacion("ejercicios", "Agrega al menos un ejercicio.")
    if len(claves) > MAXIMO_DE_EJERCICIOS:
        raise ErrorDeValidacion("ejercicios", f"Una rutina admite máximo {MAXIMO_DE_EJERCICIOS} ejercicios.")
    if len(set(claves)) != len(claves):
        raise ErrorDeValidacion("ejercicios", "Un ejercicio aparece una sola vez por rutina.")


def validar_series_previstas(valor: object) -> int:
    es_entero = isinstance(valor, int) and not isinstance(valor, bool)
    if not es_entero or not SERIES_PREVISTAS_MINIMAS <= valor <= SERIES_PREVISTAS_MAXIMAS:
        raise ErrorDeValidacion(
            "series", f"Las series previstas van de {SERIES_PREVISTAS_MINIMAS} a {SERIES_PREVISTAS_MAXIMAS}."
        )
    return valor


def nombre_de_copia(original: str, existentes: list[str]) -> str:
    """RF-002-21 y plan 002, sección 6: "Pecho (copia)", luego "(copia 2)", "(copia 3)"...

    Los nombres se comparan sin mayúsculas ni tildes, igual que la unicidad de
    la rutina. El original se recorta si hace falta para no pasar de 50 caracteres.
    """
    ocupados = {clave_de_ejercicio(nombre) for nombre in existentes}
    numero = 1
    while True:
        sufijo = " (copia)" if numero == 1 else f" (copia {numero})"
        candidato = original[: LARGO_MAXIMO_NOMBRE_DE_RUTINA - len(sufijo)].rstrip() + sufijo
        if clave_de_ejercicio(candidato) not in ocupados:
            return candidato
        numero += 1
