from django.urls import path

from . import vistas

app_name = "progreso"

urlpatterns = [
    path("", vistas.Progreso.as_view(), name="progreso"),
    path("evolucion/", vistas.Evolucion.as_view(), name="evolucion"),
    path("meta/", vistas.Meta.as_view(), name="meta"),
]
