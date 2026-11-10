"""Panel del dueño: crear cuentas y restablecer contraseñas (RNF-ACC-05, RNF-ACC-09).

El panel nunca pide ni muestra contraseñas. Al crear una cuenta o
restablecerla, genera una temporal y la muestra una sola vez.
"""

from django import forms
from django.contrib import admin, messages

from . import servicios
from .models import MAXIMO_DE_CUENTAS, Usuario


class FormularioDeCuentaNueva(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("usuario", "correo", "nombre")

    def clean(self):
        datos = super().clean()
        if not Usuario.objects.hay_cupo():
            raise forms.ValidationError(
                f"Ya existe el máximo de {MAXIMO_DE_CUENTAS} cuentas. Elimina una para crear otra."
            )
        return datos


@admin.register(Usuario)
class AdministracionDeCuentas(admin.ModelAdmin):
    list_display = ("usuario", "nombre", "correo", "is_active", "debe_cambiar_contrasena", "last_login")
    search_fields = ("usuario", "correo", "nombre")
    ordering = ("usuario",)
    actions = ("restablecer_contrasena",)

    # Al editar: los datos de la persona y si la cuenta está activa. Nada de contraseñas ni permisos.
    fields = ("usuario", "correo", "nombre", "is_active", "debe_cambiar_contrasena", "last_login", "creada")
    readonly_fields = ("debe_cambiar_contrasena", "last_login", "creada")

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = FormularioDeCuentaNueva
            kwargs["fields"] = FormularioDeCuentaNueva.Meta.fields
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        return FormularioDeCuentaNueva.Meta.fields if obj is None else self.fields

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
            return

        cuenta, temporal = servicios.invitar(usuario=obj.usuario, correo=obj.correo, nombre=obj.nombre)
        # El panel sigue trabajando con `obj`: debe apuntar a la cuenta recién creada.
        obj.pk = cuenta.pk
        obj._state.adding = False
        self._mostrar_temporal(request, cuenta, temporal)

    @admin.action(description="Restablecer contraseña (genera una temporal)")
    def restablecer_contrasena(self, request, queryset):
        for cuenta in queryset:
            self._mostrar_temporal(request, cuenta, servicios.restablecer_contrasena(cuenta))

    @staticmethod
    def _mostrar_temporal(request, cuenta, temporal: str) -> None:
        messages.warning(
            request,
            f"Cuenta {cuenta.usuario}. Contraseña temporal: {temporal} "
            "Cópiala ahora y entrégasela a la persona: no se volverá a mostrar.",
        )
