"""Vistas propias del proyecto, que no pertenecen a ninguna funcionalidad."""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def salud(request: HttpRequest) -> JsonResponse:
    """Indica que el servidor está arriba. No toca la base de datos ni revela nada."""
    return JsonResponse({"estado": "ok"})
