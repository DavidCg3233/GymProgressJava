"""Huella de los datos guardados (spec 008 · T-008-15 · RNF-008-04).

Saca un resumen de cada fila de sesiones, ejercicios de sesión, series, rutinas y
sus ejercicios, para comparar antes y después de un cambio y probar que no se
perdió ni se cambió nada sin querer.

    python manage.py huella_de_datos > antes.json
    ... recorrido ...
    python manage.py huella_de_datos --comparar antes.json

No escribe nada en la base. Solo lee.
"""

import hashlib
import json

from django.core.management.base import BaseCommand

from rutinas.models import Rutina, RutinaEjercicio
from sesiones.models import Serie, Sesion, SesionEjercicio

TABLAS = {
    "sesiones": (Sesion, ["usuario_id", "rutina_id", "nombre", "inicio", "fin", "nota"]),
    "ejercicios_de_sesion": (SesionEjercicio, ["sesion_id", "nombre", "clave", "grupo", "orden", "nota"]),
    "series": (Serie, ["ejercicio_id", "numero", "peso", "reps", "confirmada"]),
    "rutinas": (Rutina, ["usuario_id", "nombre", "dias"]),
    "ejercicios_de_rutina": (RutinaEjercicio, ["rutina_id", "ejercicio_id", "orden", "series", "reps", "peso"]),
}


def huella() -> dict:
    resultado = {}
    for tabla, (Modelo, campos) in TABLAS.items():
        filas = {}
        for fila in Modelo.objects.values("pk", *campos):
            contenido = json.dumps([str(fila[campo]) for campo in campos], ensure_ascii=False)
            filas[str(fila["pk"])] = hashlib.sha256(contenido.encode()).hexdigest()[:16]
        resultado[tabla] = filas
    return resultado


def comparar(antes: dict, despues: dict) -> dict:
    informe = {}
    for tabla in TABLAS:
        viejas, nuevas = antes.get(tabla, {}), despues.get(tabla, {})
        informe[tabla] = {
            "antes": len(viejas),
            "despues": len(nuevas),
            "agregadas": sorted(set(nuevas) - set(viejas)),
            "quitadas": sorted(set(viejas) - set(nuevas)),
            "cambiadas": sorted(pk for pk in set(viejas) & set(nuevas) if viejas[pk] != nuevas[pk]),
        }
    return informe


class Command(BaseCommand):
    help = "Huella de sesiones, series y rutinas, o la comparación con una anterior."

    def add_arguments(self, parser):
        parser.add_argument("--comparar", help="Archivo JSON con una huella anterior")

    def handle(self, *args, comparar_con=None, **opciones):
        actual = huella()
        if opciones.get("comparar"):
            with open(opciones["comparar"], encoding="utf-8") as archivo:
                antes = json.load(archivo)
            self.stdout.write(json.dumps(comparar(antes, actual), indent=2, ensure_ascii=False))
        else:
            self.stdout.write(json.dumps(actual, indent=2))
