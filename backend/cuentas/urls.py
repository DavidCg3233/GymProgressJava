from django.urls import path

from . import vistas

app_name = "cuentas"

# A propósito no hay ruta de registro ni de recuperación por correo:
# las cuentas las crea el dueño (RNF-ACC-05, RNF-ACC-09, RNF-PLA-04).
urlpatterns = [
    path("", vistas.estado, name="estado"),
    path("entrar/", vistas.entrar, name="entrar"),
    path("salir/", vistas.salir, name="salir"),
    path("contrasena/", vistas.cambiar_contrasena, name="cambiar_contrasena"),
]
