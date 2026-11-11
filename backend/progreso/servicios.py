"""Progreso: solo lee sesiones y catálogo; las cuentas están en `reglas.progreso` (plan 004)."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from django.db.models import Exists, F, OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone

from reglas import progreso as reglas
from reglas.ejercicios import clave_de_ejercicio
from reglas.progreso import SerieHecha, validar_meta
from rutinas.models import GrupoMuscular
from sesiones.models import Serie, Sesion
from sesiones.servicios import NoEncontrado


def fijar_meta(usuario, valor) -> int | None:
    """RF-004-11: fija, cambia o quita (con None) la meta semanal."""
    usuario.meta_semanal = validar_meta(valor)
    usuario.save(update_fields=["meta_semanal"])
    return usuario.meta_semanal


# --- Qué cuenta (plan 004, 4.1 y 4.2) ---------------------------------------


@dataclass(frozen=True)
class Fila:
    """Una serie que cuenta, con lo necesario para agruparla."""

    clave: str  # identidad del ejercicio: la del catálogo hoy o, si ya no está, la copiada
    nombre: str
    grupo: str
    sesion: object
    fecha: date  # día local en que empezó la sesión (RN-004-02)
    serie: SerieHecha


def _filas(usuario) -> list[Fila]:
    """RN-004-01: series confirmadas de sesiones terminadas, de la más antigua a la más nueva.

    Quien llama debe haber puesto al día las sesiones (cierre a las 2 horas).
    """
    consulta = (
        Serie.objects.filter(confirmada=True, ejercicio__sesion__usuario=usuario, ejercicio__sesion__fin__isnull=False)
        # RN-004-10: si el ejercicio sigue en el catálogo manda lo de hoy; si no, lo que se copió.
        .annotate(
            identidad=Coalesce("ejercicio__ejercicio__clave", "ejercicio__clave"),
            nombre_actual=Coalesce("ejercicio__ejercicio__nombre", "ejercicio__nombre"),
            grupo_actual=Coalesce("ejercicio__ejercicio__grupo__nombre", "ejercicio__grupo"),
            id_sesion=F("ejercicio__sesion_id"),
            inicio=F("ejercicio__sesion__inicio"),
            orden=F("ejercicio__orden"),
        )
        .order_by("inicio", "orden", "numero")
        .values("peso", "reps", "numero", "identidad", "nombre_actual", "grupo_actual", "id_sesion", "inicio", "orden")
    )
    return [
        Fila(
            clave=fila["identidad"],
            nombre=fila["nombre_actual"],
            grupo=fila["grupo_actual"],
            sesion=fila["id_sesion"],
            fecha=timezone.localtime(fila["inicio"]).date(),
            serie=SerieHecha(fila["peso"], fila["reps"], (fila["inicio"], fila["orden"], fila["numero"])),
        )
        for fila in consulta
    ]


def _por_ejercicio(filas: list[Fila]) -> dict[str, list[Fila]]:
    grupos = defaultdict(list)
    for fila in filas:
        grupos[fila.clave].append(fila)
    return grupos


# --- GET /api/progreso/ -----------------------------------------------------


def resumen(usuario, ahora) -> dict:
    filas = _filas(usuario)
    if not filas:
        # RF-004-12: sin sesiones no hay gráficas ni ceros.
        return {"vacio": True, "meta": usuario.meta_semanal, "semanas": [], "grupos": [], "records": []}

    hoy = timezone.localtime(ahora).date()
    return {
        "vacio": False,
        "meta": usuario.meta_semanal,
        "semanas": _semanas(filas, hoy, usuario.meta_semanal),
        "grupos": _grupos(usuario, filas, hoy),
        "records": _records(filas),
    }


def _semanas(filas: list[Fila], hoy: date, meta: int | None) -> list[dict]:
    """RF-004-05 y 11. Solo suman sesiones con series confirmadas (plan 004, regla nueva 3)."""
    dia_de_cada_sesion = {fila.sesion: fila.fecha for fila in filas}
    return [
        {"inicio": inicio.isoformat(), "sesiones": cantidad, "cumple": reglas.cumple(cantidad, meta)}
        for inicio, cantidad in reglas.sesiones_por_semana(dia_de_cada_sesion.values(), hoy)
    ]


def _grupos(usuario, filas: list[Fila], hoy: date) -> list[dict]:
    """RF-004-06: series de esta semana por grupo, con todos los grupos del catálogo."""
    # Se agrupa por clave para que "pecho" copiado y "Pecho" del catálogo sean uno.
    nombres = {grupo.clave: grupo.nombre for grupo in GrupoMuscular.objects.filter(usuario=usuario)}
    conteos = dict.fromkeys(nombres, 0)
    lunes = reglas.inicio_de_semana(hoy)
    for fila in filas:
        if fila.fecha >= lunes:
            clave = clave_de_ejercicio(fila.grupo)
            nombres.setdefault(clave, fila.grupo)
            conteos[clave] = conteos.get(clave, 0) + 1
    ordenados = reglas.ordenar_grupos({nombres[clave]: cantidad for clave, cantidad in conteos.items()})
    return [{"nombre": nombre, "series": cantidad} for nombre, cantidad in ordenados]


def _records(filas: list[Fila]) -> list[dict]:
    """RF-004-04: un récord por ejercicio, ordenados por nombre."""
    records = []
    for clave, suyas in _por_ejercicio(filas).items():
        series = [fila.serie for fila in suyas]
        mejor = reglas.mejor_serie(series)
        fecha = next(fila.fecha for fila in suyas if fila.serie is mejor)
        records.append(
            {
                "clave": clave,
                "nombre": suyas[-1].nombre,
                "peso": float(mejor.peso),
                "reps": mejor.reps,
                "fecha": fecha.isoformat(),
                "peso_corporal": reglas.es_de_peso_corporal(series),
            }
        )
    return sorted(records, key=lambda record: clave_de_ejercicio(record["nombre"]))


# --- GET /api/progreso/evolucion/ -------------------------------------------


def evolucion(usuario, clave) -> dict:
    """RF-004-09: un punto por sesión en la que se hizo el ejercicio, en orden de fecha."""
    suyas = _por_ejercicio(_filas(usuario)).get(clave) if isinstance(clave, str) else None
    if not suyas:
        raise NoEncontrado()

    peso_corporal = reglas.es_de_peso_corporal([fila.serie for fila in suyas])
    por_sesion: dict[object, list[Fila]] = defaultdict(list)
    for fila in suyas:
        por_sesion[fila.sesion].append(fila)

    puntos = []
    for filas_de_la_sesion in por_sesion.values():
        series = [fila.serie for fila in filas_de_la_sesion]
        pesada = reglas.mejor_serie(series)
        total = reglas.volumen(series, peso_corporal)
        puntos.append(
            {
                "fecha": filas_de_la_sesion[0].fecha.isoformat(),
                "pesada": float(pesada.peso),
                "reps_de_la_pesada": pesada.reps,
                # En peso corporal el volumen son repeticiones: se queda entero.
                "volumen": total if peso_corporal else float(total),
            }
        )
    return {"nombre": suyas[-1].nombre, "peso_corporal": peso_corporal, "puntos": puntos}


# --- Inicio sin señal: recientes y rutinas hechas hoy (plan 004, 4.5) -------

SESIONES_RECIENTES = 3  # RF-004-07


def _terminadas_con_series(usuario):
    return Sesion.objects.filter(usuario=usuario, fin__isnull=False).filter(
        Exists(Serie.objects.filter(ejercicio__sesion=OuterRef("pk"), confirmada=True))
    )


def recientes(usuario) -> list[dict]:
    """RF-004-07: las 3 sesiones terminadas más recientes, con algo registrado."""
    return [
        {
            "id": str(sesion.pk),
            "nombre": sesion.nombre,
            "inicio": timezone.localtime(sesion.inicio).isoformat(),
            "rutina": str(sesion.rutina_id) if sesion.rutina_id else None,
        }
        for sesion in _terminadas_con_series(usuario).order_by("-inicio")[:SESIONES_RECIENTES]
    ]


def hechas_hoy(usuario, ahora) -> dict:
    """RF-004-10: rutinas con una sesión terminada que empezó hoy, en hora de Colombia."""
    hoy = timezone.localtime(ahora).date()
    ids = (
        _terminadas_con_series(usuario)
        .filter(inicio__date=hoy, rutina__isnull=False)
        .order_by("inicio")
        .values_list("rutina_id", flat=True)
    )
    return {"fecha": hoy.isoformat(), "rutinas": list(dict.fromkeys(str(id) for id in ids))}
