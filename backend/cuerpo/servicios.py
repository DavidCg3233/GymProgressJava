"""Peso corporal: registrar, corregir, eliminar y resumir (spec 003, plan 003 sección 4).

Las cuentas están en `reglas.cuerpo`; aquí solo se lee y se escribe.
"""

import re
from datetime import date

from django.db import transaction
from django.utils import timezone

from reglas import cuerpo as reglas
from reglas.errores import ErrorDeValidacion
from sesiones.servicios import Conflicto, NoEncontrado

from .models import RegistroDePeso

_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


def _hoy(ahora) -> date:
    """El día de hoy en Colombia, como en la spec 004 (plan 003, sección 9)."""
    return timezone.localtime(ahora).date()


def _fecha_de_la_direccion(texto: str) -> date:
    """Una fecha mal escrita en la dirección no es un registro: responde 404 (plan 003, 4.2)."""
    if not _FECHA.fullmatch(texto):
        raise NoEncontrado()
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise NoEncontrado() from None


def _kg(peso) -> str:
    return f"{peso:.1f}".replace(".", ",")


@transaction.atomic
def registrar(usuario, texto_fecha: str, peso, reemplazar, ahora) -> RegistroDePeso:
    """RF-003-01, 02, 10 y 13. Sin `reemplazar`, no pisa el registro del día: responde 409."""
    fecha = reglas.validar_fecha_de_peso(_fecha_de_la_direccion(texto_fecha), _hoy(ahora))
    peso = reglas.validar_peso_corporal(peso)
    if not isinstance(reemplazar, bool):
        raise ErrorDeValidacion("reemplazar", "No pudimos entender la petición.")

    existente = RegistroDePeso.objects.select_for_update().filter(usuario=usuario, fecha=fecha).first()
    if existente is None:
        return RegistroDePeso.objects.create(usuario=usuario, fecha=fecha, peso=peso)
    if not reemplazar:
        raise Conflicto(f"Ya registraste {_kg(existente.peso)} kg ese día.", peso=float(existente.peso))
    existente.peso = peso
    existente.save(update_fields=["peso"])
    return existente


def eliminar(usuario, texto_fecha: str) -> None:
    """RF-003-11. La confirmación la pide la pantalla antes (RNF-USA-04)."""
    eliminados, _ = RegistroDePeso.objects.filter(usuario=usuario, fecha=_fecha_de_la_direccion(texto_fecha)).delete()
    if not eliminados:
        raise NoEncontrado()


def fijar_estatura(usuario, valor) -> int:
    """RF-003-12: se guarda una vez en la cuenta y se puede cambiar."""
    usuario.estatura_cm = reglas.validar_estatura(valor)
    usuario.save(update_fields=["estatura_cm"])
    return usuario.estatura_cm


def fijar_objetivo(usuario, valor):
    """RN-003-07: opcional, con el mismo rango que el peso. None lo quita."""
    if valor is None:
        usuario.peso_objetivo = None
    else:
        try:
            usuario.peso_objetivo = reglas.validar_peso_corporal(valor)
        except ErrorDeValidacion as error:
            raise ErrorDeValidacion("objetivo", error.mensaje) from None
    usuario.save(update_fields=["peso_objetivo"])
    return usuario.peso_objetivo


def historial(usuario) -> list[RegistroDePeso]:
    """RF-003-06: del más reciente al más antiguo."""
    return list(RegistroDePeso.objects.filter(usuario=usuario).order_by("-fecha"))


def resumen(usuario, registros: list[RegistroDePeso]) -> dict | None:
    """RF-003-03 a 09 (plan 003, 4.3). Sin registros no hay nada que resumir."""
    if not registros:
        return None
    actual = registros[0]

    cambio = None
    if len(registros) > 1:
        kg, direccion = reglas.cambio(registros[1].peso, actual.peso)
        cambio = {"kg": float(kg), "direccion": direccion}

    imc = None
    if usuario.estatura_cm:
        exacto = reglas.imc(actual.peso, usuario.estatura_cm)
        imc = {"valor": float(reglas.imc_para_mostrar(exacto)), "categoria": reglas.categoria_de_imc(exacto)}

    objetivo = None
    if usuario.peso_objetivo is not None:
        avance = reglas.hacia_el_objetivo(registros[-1].peso, actual.peso, usuario.peso_objetivo)
        objetivo = {**avance, "faltan": float(avance["faltan"])}

    return {"actual": float(actual.peso), "fecha": actual.fecha.isoformat(), "cambio": cambio, "imc": imc, "objetivo": objetivo}
