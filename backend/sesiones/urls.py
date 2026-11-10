from django.urls import path

from . import vistas

app_name = "sesiones"

urlpatterns = [
    path("arranque/", vistas.Arranque.as_view(), name="arranque"),
    path("sesiones/", vistas.Historial.as_view(), name="historial"),
    path("sesiones/<uuid:id>/", vistas.DetalleDeSesion.as_view(), name="sesion"),
    path("sesiones/<uuid:id_sesion>/ejercicios/<uuid:id>/", vistas.EjercicioDeSesion.as_view(), name="ejercicio"),
    path("series/<uuid:id>/", vistas.DetalleDeSerie.as_view(), name="serie"),
]
