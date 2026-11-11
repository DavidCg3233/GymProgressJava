"""Vistas propias del proyecto, que no pertenecen a ninguna funcionalidad."""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@require_GET
def salud(request: HttpRequest) -> JsonResponse:
    """Indica que el servidor está arriba. No toca la base de datos ni revela nada."""
    return JsonResponse({"estado": "ok"})


@require_GET
@never_cache
def pantalla(request: HttpRequest) -> HttpResponse:
    """Entrega la app (frontend/dist/index.html).

    Nunca se guarda en caché: así una versión nueva llega en la siguiente
    apertura. Los demás archivos de la app (estilos, scripts con su huella en
    el nombre, íconos, service worker) los entrega WhiteNoise.
    """
    indice = settings.PANTALLA_DIR / "index.html"
    if not indice.is_file():
        return HttpResponse(
            "La pantalla no está compilada. Corre `npm run build` en frontend/.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )
    return HttpResponse(indice.read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
