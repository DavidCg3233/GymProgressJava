"""Rutas del servidor."""

from django.urls import include, path

from . import vistas

urlpatterns = [
    path("salud/", vistas.salud, name="salud"),
    path("api/acceso/", include("cuentas.urls")),
]
