"""Progreso: solo lee sesiones y catálogo; las cuentas están en `reglas.progreso` (plan 004)."""

from reglas.progreso import validar_meta


def fijar_meta(usuario, valor) -> int | None:
    """RF-004-11: fija, cambia o quita (con None) la meta semanal."""
    usuario.meta_semanal = validar_meta(valor)
    usuario.save(update_fields=["meta_semanal"])
    return usuario.meta_semanal
