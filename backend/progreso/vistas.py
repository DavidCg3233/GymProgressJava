"""API de progreso (plan 004, sección 4.4).

Las vistas no deciden nada: leen la petición, llaman a un servicio y dan
forma a la respuesta. Permisos y errores se resuelven en `config/api.py`.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from reglas.errores import ErrorDeValidacion
from reglas.progreso import META_MAXIMA, META_MINIMA

from . import servicios


class Meta(APIView):
    def put(self, request):
        datos = request.data
        if not isinstance(datos, dict) or "meta" not in datos:
            raise ErrorDeValidacion("meta", f"La meta va de {META_MINIMA} a {META_MAXIMA} sesiones por semana.")
        return Response({"meta": servicios.fijar_meta(request.user, datos["meta"])})
