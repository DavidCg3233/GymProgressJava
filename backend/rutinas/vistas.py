"""API del catálogo y las rutinas (plan 002, sección 4.4).

Las vistas no deciden nada: leen la petición, llaman a un servicio y dan
forma a la respuesta. Permisos y errores se resuelven en `config/api.py`.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reglas import rutinas as reglas_de_rutinas
from reglas.errores import ErrorDeValidacion

from . import servicios
from .models import Ejercicio, GrupoMuscular, Rutina


class VistaConDatos(APIView):
    def datos(self) -> dict:
        if not isinstance(self.request.data, dict):
            raise ErrorDeValidacion("cuerpo", "No pudimos entender la petición.")
        return self.request.data


class Catalogo(VistaConDatos):
    def get(self, request):
        grupos, ejercicios = servicios.catalogo(request.user)
        return Response({"grupos": [grupo_json(g) for g in grupos], "ejercicios": [ejercicio_json(e) for e in ejercicios]})


class DetalleDeGrupo(VistaConDatos):
    def put(self, request, id):
        grupo = servicios.guardar_grupo(request.user, id, self.datos().get("nombre"))
        return Response({"grupo": grupo_json(grupo)})

    def delete(self, request, id):
        servicios.eliminar_grupo(request.user, id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DetalleDeEjercicio(VistaConDatos):
    def put(self, request, id):
        datos = self.datos()
        ejercicio = servicios.guardar_ejercicio(request.user, id, datos.get("nombre"), datos.get("grupo"))
        return Response({"ejercicio": ejercicio_json(ejercicio)})

    def delete(self, request, id):
        eliminadas = servicios.eliminar_ejercicio(request.user, id)
        return Response({"rutinas_eliminadas": [{"id": str(r.pk), "nombre": r.nombre} for r in eliminadas]})


class UsoDeEjercicio(VistaConDatos):
    def get(self, request, id):
        uso = servicios.uso_de_ejercicio(request.user, id)
        return Response(
            {"rutinas": [{"id": str(r.pk), "nombre": r.nombre, "quedaria_vacia": vacia} for r, vacia in uso]}
        )


class Rutinas(VistaConDatos):
    def get(self, request):
        return Response({"rutinas": [rutina_json(r) for r in servicios.listar_rutinas(request.user)]})


class DetalleDeRutina(VistaConDatos):
    def put(self, request, id):
        datos = self.datos()
        rutina = servicios.guardar_rutina(
            request.user, id, datos.get("nombre"), datos.get("dias"), datos.get("ejercicios")
        )
        return Response({"rutina": rutina_json(rutina)})

    def delete(self, request, id):
        servicios.eliminar_rutina(request.user, id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DuplicarRutina(VistaConDatos):
    def post(self, request, id):
        copia = servicios.duplicar_rutina(request.user, id, self.datos().get("id_copia"))
        return Response({"rutina": rutina_json(copia)})


# --- Forma de las respuestas (también la usa el arranque) -------------------


def grupo_json(grupo: GrupoMuscular) -> dict:
    return {"id": str(grupo.pk), "nombre": grupo.nombre}


def ejercicio_json(ejercicio: Ejercicio) -> dict:
    return {"id": str(ejercicio.pk), "nombre": ejercicio.nombre, "grupo": str(ejercicio.grupo_id)}


def rutina_json(rutina: Rutina) -> dict:
    return {
        "id": str(rutina.pk),
        "nombre": rutina.nombre,
        "dias": reglas_de_rutinas.bits_a_dias(rutina.dias),
        "ejercicios": [
            {
                "ejercicio": str(previsto.ejercicio_id),
                "nombre": previsto.ejercicio.nombre,
                "grupo": previsto.ejercicio.grupo.nombre,
                "series": previsto.series,
                "reps": previsto.reps,
                "peso": float(previsto.peso),
            }
            for previsto in rutina.ejercicios.select_related("ejercicio__grupo")
        ],
    }
