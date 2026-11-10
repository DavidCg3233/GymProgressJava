"""Rutas del servidor."""

from django.urls import path

from . import vistas

urlpatterns = [
    path("salud/", vistas.salud, name="salud"),
]
