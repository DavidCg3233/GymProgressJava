"""Las reglas de negocio viven solas (constitución P5, RNF-MAN-03).

Si este archivo falla, alguien hizo que las reglas dependan del framework,
de la base de datos o de la red, y dejaron de poder probarse aisladas.
"""

import ast
from pathlib import Path

import reglas

MODULOS_PROHIBIDOS = ("django", "rest_framework", "psycopg", "requests", "config")


def test_el_paquete_de_reglas_no_importa_framework_ni_base_de_datos():
    carpeta = Path(reglas.__file__).parent
    infracciones = []

    for archivo in sorted(carpeta.glob("*.py")):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                nombres = [alias.name for alias in nodo.names]
            elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0:
                nombres = [nodo.module or ""]
            else:
                continue
            for nombre in nombres:
                if nombre.split(".")[0] in MODULOS_PROHIBIDOS:
                    infracciones.append(f"{archivo.name} importa {nombre}")

    assert infracciones == []
