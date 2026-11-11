from django.urls import path

from . import vistas

app_name = "progreso"

urlpatterns = [
    path("meta/", vistas.Meta.as_view(), name="meta"),
]
