"""API de sesiones de entrenamiento (plan 006, sección 4.3).

Las vistas no deciden nada: leen la petición, llaman a un servicio y dan
forma a la respuesta. Los permisos y los errores se resuelven en `config/api.py`.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reglas import sesiones as reglas_de_sesiones
from reglas.errores import ErrorDeValidacion

from progreso import servicios as servicios_de_progreso
from rutinas import servicios as servicios_de_rutinas
from rutinas.vistas import ejercicio_json, grupo_json, rutina_json

from . import servicios
from .models import Serie, Sesion, SesionEjercicio


class VistaDeSesiones(APIView):
    """Antes de atender cualquier petición, pone al día las sesiones de la cuenta."""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)  # aquí se comprueban acceso y permisos
        self.ahora = timezone.now()
        servicios.poner_al_dia(request.user, self.ahora)

    def datos(self) -> dict:
        if not isinstance(self.request.data, dict):
            raise ErrorDeValidacion("cuerpo", "No pudimos entender la petición.")
        return self.request.data


class Arranque(VistaDeSesiones):
    """Todo lo que el celular necesita guardar para trabajar sin conexión (RF-006-17)."""

    def get(self, request):
        en_curso = servicios.sesion_en_curso(request.user)
        return Response(
            {
                "sesion_en_curso": _sesion_completa(en_curso, self.ahora) if en_curso else None,
                # Plan 002, 4.5: para empezar una sesión desde una rutina sin señal.
                "catalogo": _catalogo(request.user),
                "rutinas": [rutina_json(rutina) for rutina in servicios_de_rutinas.listar_rutinas(request.user)],
                # Plan 004, 4.5: el inicio funciona sin señal (RNF-004-01).
                "recientes": servicios_de_progreso.recientes(request.user),
                "hechas_hoy": servicios_de_progreso.hechas_hoy(request.user, self.ahora),
                # Spec 008, 4.2: la referencia de rutinas y sesiones, también sin señal.
                "records": servicios_de_progreso.records_por_clave(request.user),
                "ultima_vez": {
                    clave: {
                        "nombre": resumen["nombre"],
                        "grupo": resumen["grupo"],
                        "nota": resumen["nota"],
                        "series": [
                            {"numero": serie.numero, "peso": float(serie.peso), "reps": serie.reps}
                            for serie in resumen["series"]
                        ],
                    }
                    for clave, resumen in servicios.ultima_vez(request.user).items()
                },
            }
        )


class Historial(VistaDeSesiones):
    def get(self, request):
        sesiones, hay_mas = servicios.historial(request.user, _pagina(request))
        return Response({"sesiones": [_sesion_resumida(sesion) for sesion in sesiones], "hay_mas": hay_mas})


class DetalleDeSesion(VistaDeSesiones):
    def get(self, request, id):
        return Response({"sesion": _sesion_completa(servicios.obtener_sesion(request.user, id), self.ahora)})

    def put(self, request, id):
        datos = self.datos()
        sesion = servicios.guardar_sesion(
            request.user,
            id,
            nombre=datos.get("nombre"),
            inicio=datos.get("inicio"),
            fin=datos.get("fin"),
            nota=datos.get("nota"),
            ahora=self.ahora,
            rutina=datos.get("rutina"),
        )
        if sesion is None:
            return Response({"sesion": None, "descartada": True})
        return Response({"sesion": _sesion_completa(sesion, self.ahora)})

    def delete(self, request, id):
        servicios.eliminar_sesion(request.user, id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EjercicioDeSesion(VistaDeSesiones):
    def put(self, request, id_sesion, id):
        datos = self.datos()
        ejercicio = servicios.guardar_ejercicio(
            request.user,
            id_sesion,
            id,
            nombre=datos.get("nombre"),
            grupo=datos.get("grupo"),
            orden=datos.get("orden"),
            nota=datos.get("nota"),
            momento=datos.get("momento"),
            ahora=self.ahora,
        )
        return Response({"ejercicio": _ejercicio(ejercicio)})


class DetalleDeSerie(VistaDeSesiones):
    def put(self, request, id):
        datos = self.datos()
        serie = servicios.guardar_serie(
            request.user,
            id,
            id_ejercicio=datos.get("ejercicio"),
            numero=datos.get("numero"),
            peso=datos.get("peso"),
            reps=datos.get("reps"),
            confirmada=datos.get("confirmada"),
            momento=datos.get("momento"),
            ahora=self.ahora,
        )
        return Response({"serie": _serie(serie)})

    def delete(self, request, id):
        momento = request.data.get("momento") if isinstance(request.data, dict) else None
        servicios.eliminar_serie(request.user, id, momento=momento, ahora=self.ahora)
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Forma de las respuestas ------------------------------------------------


def _pagina(request) -> int:
    try:
        return int(request.query_params.get("pagina", 1))
    except ValueError:
        return 1


def _sesion_resumida(sesion: Sesion) -> dict:
    return {
        "id": str(sesion.pk),
        "nombre": sesion.nombre,
        "inicio": sesion.inicio.isoformat(),
        "fin": sesion.fin.isoformat(),
        "ejercicios": sesion.total_de_ejercicios,
        "series": sesion.total_de_series,
    }


def _sesion_completa(sesion: Sesion, ahora) -> dict:
    en_curso = sesion.fin is None and not reglas_de_sesiones.debe_cerrarse(sesion.inicio, ahora)
    return {
        "id": str(sesion.pk),
        "nombre": sesion.nombre,
        "inicio": sesion.inicio.isoformat(),
        "fin": sesion.fin.isoformat() if sesion.fin else None,
        "nota": sesion.nota,
        "rutina": str(sesion.rutina_id) if sesion.rutina_id else None,
        "en_curso": en_curso,
        "ejercicios": [_ejercicio(ejercicio) for ejercicio in sesion.ejercicios.prefetch_related("series")],
    }


def _ejercicio(ejercicio: SesionEjercicio) -> dict:
    return {
        "id": str(ejercicio.pk),
        "nombre": ejercicio.nombre,
        "grupo": ejercicio.grupo,
        "orden": ejercicio.orden,
        "nota": ejercicio.nota,
        "series": [_serie(serie) for serie in ejercicio.series.all()],
    }


def _serie(serie: Serie) -> dict:
    return {
        "id": str(serie.pk),
        "numero": serie.numero,
        "peso": float(serie.peso),
        "reps": serie.reps,
        "confirmada": serie.confirmada,
    }


def _catalogo(usuario) -> dict:
    grupos, ejercicios = servicios_de_rutinas.catalogo(usuario)
    return {"grupos": [grupo_json(g) for g in grupos], "ejercicios": [ejercicio_json(e) for e in ejercicios]}
