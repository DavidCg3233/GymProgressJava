from django.urls import path

from . import vistas

app_name = "cuentas"

urlpatterns = [
    path("", vistas.estado, name="estado"),
    path("entrar/", vistas.entrar, name="entrar"),
    path("salir/", vistas.salir, name="salir"),
]
