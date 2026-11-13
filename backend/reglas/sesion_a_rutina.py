"""Una sesión se vuelve rutina (spec 008 · RN-008-05, 06, 07 · plan 008, sección 4.1).

Funciones puras: reciben los ejercicios de la sesión con sus series
confirmadas y lo previsto en la rutina, y no saben nada de la base de datos.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from .errores import ErrorDeValidacion
from .progreso import mejor_serie, supera
from .rutinas import MAXIMO_DE_EJERCICIOS, SERIES_PREVISTAS_MAXIMAS


@dataclass(frozen=True)
class Previsto:
    """Un ejercicio dentro de una rutina: cuántas series y con qué peso y reps."""

    clave: str
    nombre: str
    grupo: str
    series: int
    peso: Decimal
    reps: int


@dataclass(frozen=True)
class Cambio:
    """Una línea de la vista previa al actualizar una rutina (RF-008-07)."""

    tipo: str  # "agrega", "mejora" o "igual"
    nombre: str
    antes: tuple[Decimal, int] | None
    despues: tuple[Decimal, int]


def ejercicios_de_sesion(ejercicios: Iterable[dict]) -> list[Previsto]:
    """RN-008-05: un ejercicio por clave, en el orden en que apareció por primera vez.

    Cada uno con sus series confirmadas sumadas (máximo 10) y su mejor serie.
    `ejercicios`: dicts con clave, nombre, grupo y `series` (solo las confirmadas).
    """
    por_clave: dict[str, dict] = {}
    for ejercicio in ejercicios:
        if not ejercicio["series"]:
            continue
        acumulado = por_clave.setdefault(ejercicio["clave"], {**ejercicio, "series": []})
        acumulado["series"].extend(ejercicio["series"])

    previstos = []
    for ejercicio in por_clave.values():
        mejor = mejor_serie(ejercicio["series"])
        previstos.append(
            Previsto(
                clave=ejercicio["clave"],
                nombre=ejercicio["nombre"],
                grupo=ejercicio["grupo"],
                series=min(len(ejercicio["series"]), SERIES_PREVISTAS_MAXIMAS),
                peso=mejor.peso,
                reps=mejor.reps,
            )
        )
    return previstos


def rutina_nueva(de_la_sesion: list[Previsto]) -> list[Previsto]:
    """RN-008-06: los ejercicios de la sesión, con las reglas de una rutina."""
    if not de_la_sesion:
        raise ErrorDeValidacion("ejercicios", "Esta sesión no tiene series confirmadas: no hay nada que guardar como rutina.")
    _exigir_maximo(len(de_la_sesion), "esta tiene")
    return list(de_la_sesion)


def actualizar_rutina(previstos: list[Previsto], de_la_sesion: list[Previsto]) -> tuple[list[Previsto], list[Cambio]]:
    """RN-008-07: suma lo nuevo al final y mejora lo que la sesión superó. No quita nada.

    Devuelve los previstos que quedarían y la lista de cambios para la vista previa.
    Las series previstas de un ejercicio que ya estaba no cambian.
    """
    hecho = {ejercicio.clave: ejercicio for ejercicio in de_la_sesion}
    nuevos: list[Previsto] = []
    cambios: list[Cambio] = []

    for actual in previstos:
        sesion = hecho.get(actual.clave)
        if sesion is not None and supera(sesion, actual):
            mejorado = Previsto(actual.clave, actual.nombre, actual.grupo, actual.series, sesion.peso, sesion.reps)
            nuevos.append(mejorado)
            cambios.append(Cambio("mejora", actual.nombre, (actual.peso, actual.reps), (sesion.peso, sesion.reps)))
        else:
            nuevos.append(actual)
            cambios.append(Cambio("igual", actual.nombre, (actual.peso, actual.reps), (actual.peso, actual.reps)))

    ya_estaban = {actual.clave for actual in previstos}
    for ejercicio in de_la_sesion:
        if ejercicio.clave not in ya_estaban:
            nuevos.append(ejercicio)
            cambios.append(Cambio("agrega", ejercicio.nombre, None, (ejercicio.peso, ejercicio.reps)))

    _exigir_maximo(len(nuevos), "quedaría con")
    return nuevos, cambios


def _exigir_maximo(cantidad: int, como: str) -> None:
    if cantidad > MAXIMO_DE_EJERCICIOS:
        sobran = cantidad - MAXIMO_DE_EJERCICIOS
        verbo = "sobra" if sobran == 1 else "sobran"
        raise ErrorDeValidacion(
            "ejercicios",
            f"Una rutina admite máximo {MAXIMO_DE_EJERCICIOS} ejercicios: {como} {cantidad}, {verbo} {sobran}.",
        )
