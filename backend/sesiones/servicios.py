"""Operaciones sobre sesiones de entrenamiento (spec 006).

Todas reciben la cuenta que hace la petición y solo tocan datos suyos
(RNF-ACC-06). Lo que no es suyo se trata como si no existiera.

Sobre la hora: cada acción llega con `momento`, la hora en que ocurrió en el
celular. Se decide con esa hora y no con la de llegada, para que lo
registrado sin señal se acepte aunque se sincronice horas después (RF-006-16).
"""

from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Q

from reglas import ejercicios as reglas_de_ejercicios
from reglas import series as reglas_de_series
from reglas import sesiones as reglas_de_sesiones
from reglas import textos as reglas_de_textos
from reglas.errores import ErrorDeValidacion

from .models import Serie, Sesion, SesionEjercicio

# Una sesión vencida y vacía se conserva este tiempo antes de borrarse, por si
# el celular todavía tiene series sin sincronizar.
MARGEN_DE_SINCRONIZACION = timedelta(hours=24)

SESIONES_POR_PAGINA = 20

MENSAJE_TERMINADA = "Esta sesión ya terminó y no se puede modificar."


class NoEncontrado(Exception):
    """El dato no existe o no es de quien lo pide. Hacia afuera es lo mismo."""


class Conflicto(Exception):
    """La operación choca con el estado actual. `mensaje` es lo que ve el usuario."""

    def __init__(self, mensaje: str, **extra) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.extra = extra


# --- Estado de las sesiones -------------------------------------------------


def poner_al_dia(usuario, ahora: datetime) -> None:
    """Cierra las sesiones que cumplieron 2 horas y limpia las vacías ya viejas.

    No hay tarea programada: se hace al atender cada petición (plan 006, 4.2).
    """
    for sesion in Sesion.objects.filter(usuario=usuario, fin__isnull=True):
        if reglas_de_sesiones.debe_cerrarse(sesion.inicio, ahora):
            sesion.fin = reglas_de_sesiones.hora_de_cierre_automatico(sesion.inicio)
            sesion.cierre_automatico = True
            # A propósito no se toca `actualizado`: debe seguir marcando la última
            # vez que el celular envió algo de esta sesión.
            sesion.save(update_fields=["fin", "cierre_automatico"])

    # RF-006-19: una sesión que terminó sin series confirmadas se descarta.
    # El margen cuenta desde la última vez que el celular la envió, no desde su
    # fin: una sesión de hace días que apenas se sincroniza aún espera sus series.
    (
        Sesion.objects.filter(
            usuario=usuario, cierre_automatico=True, actualizado__lt=ahora - MARGEN_DE_SINCRONIZACION
        )
        .exclude(_con_series_confirmadas())
        .delete()
    )


def _con_series_confirmadas() -> Exists:
    return Exists(Serie.objects.filter(ejercicio__sesion=OuterRef("pk"), confirmada=True))


def _visibles(usuario):
    """Lo que el usuario puede ver: su sesión en curso y las terminadas con algo registrado."""
    return Sesion.objects.filter(usuario=usuario).filter(Q(fin__isnull=True) | _con_series_confirmadas())


def sesion_en_curso(usuario) -> Sesion | None:
    return Sesion.objects.filter(usuario=usuario, fin__isnull=True).first()


def obtener_sesion(usuario, id) -> Sesion:
    sesion = _visibles(usuario).filter(pk=id).first()
    if sesion is None:
        raise NoEncontrado()
    return sesion


def historial(usuario, pagina: int) -> tuple[list[Sesion], bool]:
    """Sesiones terminadas, de la más reciente a la más antigua (RF-006-09)."""
    terminadas = (
        _visibles(usuario)
        .filter(fin__isnull=False)
        .annotate(
            total_de_ejercicios=Count("ejercicios", distinct=True),
            total_de_series=Count("ejercicios__series", filter=Q(ejercicios__series__confirmada=True), distinct=True),
        )
        .order_by("-fin")
    )
    desde = (max(pagina, 1) - 1) * SESIONES_POR_PAGINA
    # Se pide una de más para saber si hay otra página sin contar todo.
    tramo = list(terminadas[desde : desde + SESIONES_POR_PAGINA + 1])
    return tramo[:SESIONES_POR_PAGINA], len(tramo) > SESIONES_POR_PAGINA


# --- Guardar una sesión -----------------------------------------------------


@transaction.atomic
def guardar_sesion(usuario, id, nombre, inicio, fin, nota, ahora: datetime) -> Sesion | None:
    """Crea, actualiza o termina una sesión. Devuelve None si quedó descartada."""
    inicio = _exigir_hora(inicio, "inicio", "La hora de inicio no es válida.")
    fin = _hora_opcional(fin, "fin", "La hora de fin no es válida.")
    nombre = reglas_de_textos.nombre_de_sesion_libre(nombre)
    nota = reglas_de_textos.validar_nota(nota)
    if fin is not None:
        if fin < inicio:
            raise ErrorDeValidacion("fin", "La sesión no puede terminar antes de empezar.")
        # RN-006-12: ninguna sesión dura más de 2 horas, la cierre quien la cierre.
        fin = min(fin, reglas_de_sesiones.hora_de_cierre_automatico(inicio))

    sesion = Sesion.objects.select_for_update().filter(pk=id).first()
    if sesion is not None and sesion.usuario_id != usuario.pk:
        raise NoEncontrado()

    if sesion is None:
        sesion = _crear_sesion(usuario, id, nombre, inicio, fin, nota, ahora)
    elif sesion.fin is not None and not sesion.cierre_automatico:
        # Ya la terminó el usuario: queda fija. Repetir el cierre no es un error.
        if fin is None:
            raise Conflicto(MENSAJE_TERMINADA)
        return sesion
    else:
        sesion.nombre = nombre
        sesion.nota = nota
        if fin is not None:
            sesion.fin = fin
            sesion.cierre_automatico = False
        sesion.save()

    termino_el_usuario = sesion.fin is not None and not sesion.cierre_automatico
    if termino_el_usuario and reglas_de_sesiones.debe_descartarse(_series_confirmadas(sesion)):
        sesion.delete()
        return None
    return sesion


def _crear_sesion(usuario, id, nombre, inicio, fin, nota, ahora) -> Sesion:
    cierre_automatico = False
    if fin is None:
        if reglas_de_sesiones.debe_cerrarse(inicio, ahora):
            # Empezó sin conexión hace más de 2 horas: nace cerrada, a la
            # espera de las series y del cierre que el celular aún debe enviar.
            fin = reglas_de_sesiones.hora_de_cierre_automatico(inicio)
            cierre_automatico = True
        else:
            en_curso = sesion_en_curso(usuario)
            if en_curso is not None:
                raise Conflicto("Ya tienes una sesión en curso.", sesion_en_curso=str(en_curso.pk))
    return Sesion.objects.create(
        id=id, usuario=usuario, nombre=nombre, inicio=inicio, fin=fin, nota=nota, cierre_automatico=cierre_automatico
    )


def _series_confirmadas(sesion: Sesion) -> int:
    return Serie.objects.filter(ejercicio__sesion=sesion, confirmada=True).count()


def eliminar_sesion(usuario, id) -> None:
    """Elimina una sesión terminada, con todas sus series (RF-006-15)."""
    sesion = obtener_sesion(usuario, id)
    if sesion.fin is None:
        raise Conflicto("Termina la sesión antes de eliminarla.")
    sesion.delete()


# --- Ejercicios y series ----------------------------------------------------


def _sesion_modificable(usuario, sesion: Sesion | None, momento, ahora: datetime) -> Sesion:
    """Comprueba que la sesión sea del usuario y que la acción ocurrió antes de su cierre."""
    if sesion is None or sesion.usuario_id != usuario.pk:
        raise NoEncontrado()

    momento = _hora_opcional(momento, "momento", "La hora de la acción no es válida.") or ahora
    cierre = sesion.fin or reglas_de_sesiones.hora_de_cierre_automatico(sesion.inicio)
    if momento > cierre:
        raise Conflicto(MENSAJE_TERMINADA)
    return sesion


@transaction.atomic
def guardar_ejercicio(usuario, id_sesion, id, nombre, grupo, orden, nota, momento, ahora: datetime) -> SesionEjercicio:
    """Agrega o actualiza un ejercicio de una sesión (RF-006-13, RF-006-23)."""
    sesion = _sesion_modificable(usuario, Sesion.objects.filter(pk=id_sesion).first(), momento, ahora)

    ejercicio = SesionEjercicio.objects.filter(pk=id).first()
    if ejercicio is not None and ejercicio.sesion_id != sesion.pk:
        raise NoEncontrado()

    nombre = reglas_de_ejercicios.validar_nombre_de_ejercicio(nombre)
    datos = {
        "nombre": nombre,
        "clave": reglas_de_ejercicios.clave_de_ejercicio(nombre),
        "grupo": reglas_de_ejercicios.validar_grupo_muscular(grupo),
        "orden": _validar_orden(orden),
        "nota": reglas_de_textos.validar_nota(nota),
    }
    if ejercicio is None:
        return SesionEjercicio.objects.create(id=id, sesion=sesion, **datos)

    for campo, valor in datos.items():
        setattr(ejercicio, campo, valor)
    ejercicio.save()
    return ejercicio


@transaction.atomic
def guardar_serie(usuario, id, id_ejercicio, numero, peso, reps, confirmada, momento, ahora: datetime) -> Serie:
    """Registra o corrige una serie (RF-006-03, 12, 14, 24)."""
    ejercicio = SesionEjercicio.objects.select_related("sesion").filter(pk=id_ejercicio).first()
    _sesion_modificable(usuario, ejercicio.sesion if ejercicio else None, momento, ahora)

    serie = Serie.objects.filter(pk=id).first()
    if serie is not None and serie.ejercicio_id != ejercicio.pk:
        raise NoEncontrado()

    datos = {
        "numero": reglas_de_ejercicios.validar_numero_de_serie(numero),
        "peso": reglas_de_series.validar_peso(peso),
        "reps": reglas_de_series.validar_repeticiones(reps),
        "confirmada": _validar_confirmada(confirmada),
    }
    if Serie.objects.filter(ejercicio=ejercicio, numero=datos["numero"]).exclude(pk=id).exists():
        raise ErrorDeValidacion("numero", "Ese ejercicio ya tiene una serie con ese número.")

    if serie is None:
        return Serie.objects.create(id=id, ejercicio=ejercicio, **datos)

    for campo, valor in datos.items():
        setattr(serie, campo, valor)
    serie.save()
    return serie


@transaction.atomic
def eliminar_serie(usuario, id, momento, ahora: datetime) -> None:
    """Quita una serie de una sesión en curso (RF-006-12)."""
    serie = Serie.objects.select_related("ejercicio__sesion").filter(pk=id).first()
    _sesion_modificable(usuario, serie.ejercicio.sesion if serie else None, momento, ahora)
    serie.delete()


# --- La última vez ----------------------------------------------------------


def ultima_vez(usuario) -> dict[str, dict]:
    """Lo último registrado en cada ejercicio, serie por serie (RF-006-04, RN-006-08).

    Para cada número de serie se toma la sesión terminada más reciente que la
    tenga confirmada. El nombre, el grupo y la nota salen de la sesión más
    reciente en que se hizo el ejercicio (RN-006-16).
    """
    confirmadas = (
        Serie.objects.filter(confirmada=True, ejercicio__sesion__usuario=usuario, ejercicio__sesion__fin__isnull=False)
        .select_related("ejercicio")
        .order_by("-ejercicio__sesion__fin", "numero")
    )

    por_ejercicio: dict[str, dict] = {}
    for serie in confirmadas:
        ejercicio = serie.ejercicio
        resumen = por_ejercicio.setdefault(
            ejercicio.clave,
            {"nombre": ejercicio.nombre, "grupo": ejercicio.grupo, "nota": ejercicio.nota, "series": {}},
        )
        # Van de la más reciente a la más antigua: la primera que aparece gana.
        resumen["series"].setdefault(serie.numero, serie)

    for resumen in por_ejercicio.values():
        resumen["series"] = [resumen["series"][numero] for numero in sorted(resumen["series"])]
    return por_ejercicio


# --- Validaciones propias de la API -----------------------------------------


def _exigir_hora(valor, campo: str, mensaje: str) -> datetime:
    hora = _hora_opcional(valor, campo, mensaje)
    if hora is None:
        raise ErrorDeValidacion(campo, mensaje)
    return hora


def _hora_opcional(valor, campo: str, mensaje: str) -> datetime | None:
    """Convierte un texto ISO 8601 con zona horaria. Sin zona, la hora sería ambigua."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        hora = valor
    else:
        try:
            hora = datetime.fromisoformat(valor)
        except (TypeError, ValueError):
            raise ErrorDeValidacion(campo, mensaje) from None
    if hora.tzinfo is None:
        raise ErrorDeValidacion(campo, mensaje)
    return hora


def _validar_orden(valor) -> int:
    es_entero = isinstance(valor, int) and not isinstance(valor, bool)
    if not es_entero or not 1 <= valor <= 100:
        raise ErrorDeValidacion("orden", "El orden del ejercicio no es válido.")
    return valor


def _validar_confirmada(valor) -> bool:
    if not isinstance(valor, bool):
        raise ErrorDeValidacion("confirmada", "Indica si la serie está confirmada.")
    return valor
