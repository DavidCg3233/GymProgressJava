"""API del peso corporal (plan 003, sección 4.2).

Las vistas no deciden nada: leen la petición, llaman a un servicio y dan
forma a la respuesta. Permisos y errores se resuelven en `config/api.py`.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from reglas.errores import ErrorDeValidacion

from . import servicios


class VistaDelCuerpo(APIView):
    def campo(self, nombre: str, mensaje: str):
        """El valor de un campo obligatorio, aunque sea null."""
        datos = self.request.data
        if not isinstance(datos, dict) or nombre not in datos:
            raise ErrorDeValidacion(nombre, mensaje)
        return datos[nombre]


class Peso(VistaDelCuerpo):
    def get(self, request):
        registros = servicios.historial(request.user)
        objetivo = request.user.peso_objetivo
        return Response(
            {
                "estatura": request.user.estatura_cm,
                "objetivo": float(objetivo) if objetivo is not None else None,
                "registros": [_registro(registro) for registro in registros],
                "resumen": servicios.resumen(request.user, registros),
            }
        )


class RegistroDelDia(VistaDelCuerpo):
    def put(self, request, fecha):
        datos = request.data if isinstance(request.data, dict) else {}
        registro = servicios.registrar(
            request.user, fecha, datos.get("peso"), datos.get("reemplazar", False), timezone.now()
        )
        return Response({"registro": _registro(registro)})

    def delete(self, request, fecha):
        servicios.eliminar(request.user, fecha)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Estatura(VistaDelCuerpo):
    def put(self, request):
        valor = self.campo("estatura", "La estatura va en centímetros, de 100 a 250.")
        return Response({"estatura": servicios.fijar_estatura(request.user, valor)})


class Objetivo(VistaDelCuerpo):
    def put(self, request):
        objetivo = servicios.fijar_objetivo(request.user, self.campo("objetivo", "Escribe tu peso objetivo."))
        return Response({"objetivo": float(objetivo) if objetivo is not None else None})


def _registro(registro) -> dict:
    return {"fecha": registro.fecha.isoformat(), "peso": float(registro.peso)}
