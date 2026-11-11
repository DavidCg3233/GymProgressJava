from django.urls import path

from . import vistas

app_name = "rutinas"

urlpatterns = [
    path("catalogo/", vistas.Catalogo.as_view(), name="catalogo"),
    path("catalogo/grupos/<uuid:id>/", vistas.DetalleDeGrupo.as_view(), name="grupo"),
    path("catalogo/ejercicios/<uuid:id>/", vistas.DetalleDeEjercicio.as_view(), name="ejercicio"),
    path("catalogo/ejercicios/<uuid:id>/uso/", vistas.UsoDeEjercicio.as_view(), name="uso_de_ejercicio"),
    path("rutinas/", vistas.Rutinas.as_view(), name="rutinas"),
    path("rutinas/<uuid:id>/", vistas.DetalleDeRutina.as_view(), name="rutina"),
    path("rutinas/<uuid:id>/duplicar/", vistas.DuplicarRutina.as_view(), name="duplicar_rutina"),
]
