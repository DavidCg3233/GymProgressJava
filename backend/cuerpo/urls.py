from django.urls import path

from . import vistas

app_name = "cuerpo"

# Estatura y objetivo van antes que la fecha: si no, "estatura" se leería como una fecha.
urlpatterns = [
    path("", vistas.Peso.as_view(), name="peso"),
    path("estatura/", vistas.Estatura.as_view(), name="estatura"),
    path("objetivo/", vistas.Objetivo.as_view(), name="objetivo"),
    path("<str:fecha>/", vistas.RegistroDelDia.as_view(), name="registro"),
]
