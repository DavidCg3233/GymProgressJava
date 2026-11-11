"""Operaciones sobre el catálogo y las rutinas (spec 002, plan 002 sección 4.4).

Todas reciben la cuenta que hace la petición y solo tocan datos suyos: lo
ajeno se trata como si no existiera (RNF-ACC-06).
"""

import uuid

from django.db import transaction

from reglas import ejercicios as reglas_de_ejercicios
from reglas import rutinas as reglas_de_rutinas
from reglas import series as reglas_de_series
from reglas.errores import ErrorDeValidacion
from sesiones.servicios import Conflicto, NoEncontrado

from .models import Ejercicio, GrupoMuscular, Rutina, RutinaEjercicio

MENSAJE_FUERA_DEL_CATALOGO = "Ese ejercicio no está en tu catálogo."


# --- Catálogo ---------------------------------------------------------------


def catalogo(usuario) -> tuple[list[GrupoMuscular], list[Ejercicio]]:
    return list(GrupoMuscular.objects.filter(usuario=usuario)), list(Ejercicio.objects.filter(usuario=usuario))


@transaction.atomic
def guardar_grupo(usuario, id, nombre) -> GrupoMuscular:
    """Crea o renombra un grupo muscular (RF-002-19)."""
    grupo = _propio_o_nuevo(GrupoMuscular, usuario, id)
    try:
        nombre = reglas_de_ejercicios.validar_grupo_muscular(nombre)
    except ErrorDeValidacion as error:
        raise ErrorDeValidacion("nombre", error.mensaje) from None
    _exigir_nombre_libre(GrupoMuscular, usuario, nombre, grupo, "Ya tienes un grupo con ese nombre.")

    grupo.nombre = nombre
    grupo.save()
    return grupo


def eliminar_grupo(usuario, id) -> None:
    grupo = _propio(GrupoMuscular, usuario, id)
    if grupo.ejercicios.exists():
        raise Conflicto("Mueve o elimina primero los ejercicios de este grupo.")
    grupo.delete()


@transaction.atomic
def guardar_ejercicio(usuario, id, nombre, id_grupo) -> Ejercicio:
    """Crea, renombra o cambia de grupo un ejercicio del catálogo (RF-002-09, 15)."""
    ejercicio = _propio_o_nuevo(Ejercicio, usuario, id)
    nombre = reglas_de_ejercicios.validar_nombre_de_ejercicio(nombre)
    grupo = GrupoMuscular.objects.filter(usuario=usuario, pk=_uuid(id_grupo)).first() if _uuid(id_grupo) else None
    if grupo is None:
        raise ErrorDeValidacion("grupo", "Elige el grupo muscular.")
    _exigir_nombre_libre(Ejercicio, usuario, nombre, ejercicio, "Ya tienes un ejercicio con ese nombre.")

    ejercicio.nombre = nombre
    ejercicio.grupo = grupo
    ejercicio.save()
    return ejercicio


def uso_de_ejercicio(usuario, id) -> list[tuple[Rutina, bool]]:
    """RF-002-17 y 18: en qué rutinas está, y si alguna quedaría vacía sin él."""
    ejercicio = _propio(Ejercicio, usuario, id)
    rutinas = Rutina.objects.filter(ejercicios__ejercicio=ejercicio).order_by("nombre")
    return [(rutina, rutina.ejercicios.count() == 1) for rutina in rutinas]


@transaction.atomic
def eliminar_ejercicio(usuario, id) -> list[Rutina]:
    """RF-002-16 y 18: lo quita del catálogo y de las rutinas; las que quedan vacías se eliminan.

    La pantalla ya pidió confirmación mostrando `uso_de_ejercicio`. Las sesiones
    que lo usaron conservan su copia del nombre y el grupo.
    """
    rutinas_vacias = [rutina for rutina, quedaria_vacia in uso_de_ejercicio(usuario, id) if quedaria_vacia]
    eliminadas = [Rutina(id=rutina.pk, nombre=rutina.nombre) for rutina in rutinas_vacias]
    for rutina in rutinas_vacias:
        rutina.delete()
    _propio(Ejercicio, usuario, id).delete()
    return eliminadas


# --- Rutinas ----------------------------------------------------------------


def listar_rutinas(usuario) -> list[Rutina]:
    return list(Rutina.objects.filter(usuario=usuario).prefetch_related("ejercicios__ejercicio__grupo"))


@transaction.atomic
def guardar_rutina(usuario, id, nombre, dias, ejercicios) -> Rutina:
    """Crea o reemplaza una rutina completa: todo o nada (RF-002-01, 03, 04, 05, 20)."""
    rutina = _propio_o_nuevo(Rutina, usuario, id)
    nombre = reglas_de_rutinas.validar_nombre_de_rutina(nombre)
    dias = reglas_de_rutinas.validar_dias(dias)
    previstos = _validar_previstos(usuario, ejercicios)
    _exigir_nombre_libre(Rutina, usuario, nombre, rutina, "Ya tienes una rutina con ese nombre.")

    rutina.nombre = nombre
    rutina.dias = reglas_de_rutinas.dias_a_bits(dias)
    rutina.save()
    rutina.ejercicios.all().delete()
    RutinaEjercicio.objects.bulk_create(
        RutinaEjercicio(rutina=rutina, orden=orden, **previsto) for orden, previsto in enumerate(previstos, start=1)
    )
    return rutina


def eliminar_rutina(usuario, id) -> None:
    """RF-002-06. Las sesiones de esta rutina se conservan (su enlace queda vacío)."""
    _propio(Rutina, usuario, id).delete()


@transaction.atomic
def duplicar_rutina(usuario, id, id_copia) -> Rutina:
    """RF-002-21: misma lista de ejercicios, sin días, con un nombre que no se repite."""
    original = _propio(Rutina, usuario, id)
    id_copia = _uuid(id_copia)
    if id_copia is None:
        raise ErrorDeValidacion("id_copia", "No pudimos entender la petición.")
    existente = Rutina.objects.filter(pk=id_copia).first()
    if existente is not None:
        # Repetir el mismo pedido devuelve la misma copia.
        if existente.usuario_id != usuario.pk:
            raise NoEncontrado()
        return existente

    nombres = Rutina.objects.filter(usuario=usuario).values_list("nombre", flat=True)
    copia = Rutina.objects.create(
        id=id_copia, usuario=usuario, nombre=reglas_de_rutinas.nombre_de_copia(original.nombre, list(nombres)), dias=0
    )
    RutinaEjercicio.objects.bulk_create(
        RutinaEjercicio(
            rutina=copia, ejercicio=previsto.ejercicio, orden=previsto.orden,
            series=previsto.series, reps=previsto.reps, peso=previsto.peso,
        )
        for previsto in original.ejercicios.all()
    )
    return copia


def _validar_previstos(usuario, ejercicios) -> list[dict]:
    if not isinstance(ejercicios, list):
        raise ErrorDeValidacion("ejercicios", "La lista de ejercicios no es válida.")
    if not ejercicios:
        reglas_de_rutinas.validar_ejercicios_de_rutina([])

    del_catalogo = {ejercicio.pk: ejercicio for ejercicio in Ejercicio.objects.filter(usuario=usuario)}
    previstos = []
    for dato in ejercicios:
        if not isinstance(dato, dict) or _uuid(dato.get("ejercicio")) not in del_catalogo:
            raise ErrorDeValidacion("ejercicios", MENSAJE_FUERA_DEL_CATALOGO)
        previstos.append(
            {
                "ejercicio": del_catalogo[_uuid(dato["ejercicio"])],
                "series": reglas_de_rutinas.validar_series_previstas(dato.get("series")),
                "reps": reglas_de_series.validar_repeticiones(dato.get("reps")),
                "peso": reglas_de_series.validar_peso(dato.get("peso")),
            }
        )
    reglas_de_rutinas.validar_ejercicios_de_rutina([previsto["ejercicio"].clave for previsto in previstos])
    return previstos


# --- Ayudantes --------------------------------------------------------------


def _uuid(valor) -> uuid.UUID | None:
    if isinstance(valor, uuid.UUID):
        return valor
    if not isinstance(valor, str):
        return None
    try:
        return uuid.UUID(valor)
    except ValueError:
        return None


def _propio(Modelo, usuario, id):
    objeto = Modelo.objects.filter(pk=_uuid(id), usuario=usuario).first() if _uuid(id) else None
    if objeto is None:
        raise NoEncontrado()
    return objeto


def _propio_o_nuevo(Modelo, usuario, id):
    """El objeto de la persona con ese id, o uno nuevo sin guardar. Si es de otra persona, no existe."""
    objeto = Modelo.objects.filter(pk=id).first()
    if objeto is None:
        return Modelo(id=id, usuario=usuario)
    if objeto.usuario_id != usuario.pk:
        raise NoEncontrado()
    return objeto


def _exigir_nombre_libre(Modelo, usuario, nombre, propio, mensaje) -> None:
    clave = reglas_de_ejercicios.clave_de_ejercicio(nombre)
    if Modelo.objects.filter(usuario=usuario, clave=clave).exclude(pk=propio.pk).exists():
        raise ErrorDeValidacion("nombre", mensaje)
