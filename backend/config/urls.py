"""Rutas del servidor."""

from django.contrib import admin
from django.urls import include, path

from . import vistas

admin.site.site_header = "GymProgress · Panel del dueño"
admin.site.site_title = "GymProgress"
admin.site.index_title = "Cuentas"

urlpatterns = [
    path("", vistas.pantalla, name="pantalla"),
    path("salud/", vistas.salud, name="salud"),
    path("api/acceso/", include("cuentas.urls")),
    path("api/", include("sesiones.urls")),
    path("api/", include("rutinas.urls")),
    path("panel/", admin.site.urls),
]
