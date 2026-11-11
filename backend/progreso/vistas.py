"""API de progreso (plan 004, sección 4.4).

Las vistas no deciden nada: leen la petición, llaman a un servicio y dan
forma a la respuesta. Permisos y errores se resuelven en `config/api.py`.
"""

from rest_framework.response import Response

from reglas.errores import ErrorDeValidacion
from reglas.progreso import META_MAXIMA, META_MINIMA
from sesiones.vistas import VistaDeSesiones

from . import servicios


class Progreso(VistaDeSesiones):
    """Hereda de las vistas de sesiones para cerrar antes las que pasaron las 2 horas."""

    def get(self, request):
        return Response(servicios.resumen(request.user, self.ahora))


class Evolucion(VistaDeSesiones):
    def get(self, request):
        return Response(servicios.evolucion(request.user, request.query_params.get("clave")))


class Meta(VistaDeSesiones):
    def put(self, request):
        datos = request.data
        if not isinstance(datos, dict) or "meta" not in datos:
            raise ErrorDeValidacion("meta", f"La meta va de {META_MINIMA} a {META_MAXIMA} sesiones por semana.")
        return Response({"meta": servicios.fijar_meta(request.user, datos["meta"])})
