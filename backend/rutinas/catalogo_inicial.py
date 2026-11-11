"""Catálogo predefinido (RF-002-14) y alta de ejercicios en el catálogo (RF-002-09).

Las funciones reciben las clases de los modelos como parámetro: así las usa
igual el código de la app y la migración de datos, que trabaja con versiones
"históricas" de los modelos (sin sus métodos `save`). Por eso aquí la clave
se calcula siempre a mano.
"""

import uuid

from reglas.ejercicios import clave_de_ejercicio

# Spec 002, sección 5. Aprobado por David el 2026-11-10.
# La plancha se registra con peso 0 y los segundos en el campo de repeticiones.
CATALOGO: dict[str, list[str]] = {
    "Pecho": [
        "Press de banca",
        "Press inclinado",
        "Press declinado",
        "Press con mancuernas",
        "Aperturas con mancuernas",
        "Cruce de poleas",
        "Fondos",
    ],
    "Espalda": ["Dominadas", "Jalón al pecho", "Remo con barra", "Remo con mancuerna", "Remo en polea baja", "Peso muerto"],
    "Hombro": ["Press militar", "Press Arnold", "Elevaciones laterales", "Elevaciones frontales", "Pájaros", "Face pull"],
    "Bíceps": ["Curl con barra", "Curl con mancuernas", "Curl martillo", "Curl predicador"],
    "Tríceps": ["Extensión en polea", "Press francés", "Fondos en banco", "Patada de tríceps"],
    "Pierna": [
        "Sentadilla",
        "Prensa",
        "Zancadas",
        "Extensión de cuádriceps",
        "Curl femoral",
        "Peso muerto rumano",
        "Hip thrust",
    ],
    "Pantorrilla": ["Elevación de talones de pie", "Elevación de talones sentado"],
    "Abdomen": ["Crunch", "Plancha", "Elevación de piernas", "Rueda abdominal"],
}


def cargar(usuario, GrupoMuscular, Ejercicio) -> None:
    """Agrega al catálogo de la persona lo predefinido que le falte. No pisa nada."""
    for nombre_de_grupo, ejercicios in CATALOGO.items():
        for nombre in ejercicios:
            asegurar_ejercicio(usuario, nombre, nombre_de_grupo, GrupoMuscular, Ejercicio)


def asegurar_ejercicio(usuario, nombre: str, nombre_de_grupo: str, GrupoMuscular, Ejercicio):
    """Devuelve el ejercicio de la persona con ese nombre; si no existe, lo crea con ese grupo.

    Si ya existía, se devuelve tal cual: no se le cambia el nombre ni el grupo.
    """
    clave = clave_de_ejercicio(nombre)
    existente = Ejercicio.objects.filter(usuario=usuario, clave=clave).first()
    if existente is not None:
        return existente

    clave_de_grupo = clave_de_ejercicio(nombre_de_grupo)
    grupo = GrupoMuscular.objects.filter(usuario=usuario, clave=clave_de_grupo).first()
    if grupo is None:
        grupo = GrupoMuscular.objects.create(
            id=uuid.uuid4(), usuario=usuario, nombre=nombre_de_grupo.strip(), clave=clave_de_grupo
        )
    return Ejercicio.objects.create(id=uuid.uuid4(), usuario=usuario, nombre=nombre.strip(), clave=clave, grupo=grupo)
