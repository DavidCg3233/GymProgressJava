"""Seguridad de la app publicada en Railway (plan 006, sección 2 revisada).

Todo lo que solo aplica con la app publicada vive aquí, como funciones que
las pruebas pueden revisar sin levantar un servidor.
"""

UN_ANIO_EN_SEGUNDOS = 365 * 24 * 60 * 60

# Rutas que no llevan la política de contenido: el panel de administración de
# Django usa sus propios scripts y no está pensado para ella.
_RUTAS_SIN_POLITICA = ("/panel/",)


def ajustes_https(activo: bool) -> dict:
    """RNF-SEG-02: con la app publicada, todo viaja por HTTPS y el navegador lo recuerda."""
    if not activo:
        return {"SECURE_SSL_REDIRECT": False, "SECURE_HSTS_SECONDS": 0}
    return {
        "SECURE_SSL_REDIRECT": True,
        # Railway recibe el HTTPS y le pasa la petición a Django por HTTP interno,
        # avisando en esta cabecera cómo llegó originalmente.
        "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
        # La revisión de salud de Railway llega por HTTP interno: no se redirige.
        "SECURE_REDIRECT_EXEMPT": [r"^salud/$"],
        "SECURE_HSTS_SECONDS": UN_ANIO_EN_SEGUNDOS,
        "SESSION_COOKIE_SECURE": True,
        "CSRF_COOKIE_SECURE": True,
    }


def politica_de_contenido() -> str:
    """RNF-SEG-05: la página solo carga y ejecuta recursos del mismo sitio.

    Si alguien lograra inyectar código en la página, el navegador no lo
    ejecutaría ni le dejaría enviar datos a otro sitio.
    """
    reglas = {
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self'",
        "img-src": "'self' data:",
        "connect-src": "'self'",
        "manifest-src": "'self'",
        "worker-src": "'self'",
        "object-src": "'none'",
        "base-uri": "'self'",
        "form-action": "'self'",
        "frame-ancestors": "'none'",
    }
    return "; ".join(f"{directiva} {valor}" for directiva, valor in reglas.items())


class PoliticaDeContenido:
    """Agrega la cabecera Content-Security-Policy a toda respuesta, salvo al panel."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.politica = politica_de_contenido()

    def __call__(self, request):
        respuesta = self.get_response(request)
        if not request.path.startswith(_RUTAS_SIN_POLITICA):
            respuesta.setdefault("Content-Security-Policy", self.politica)
        return respuesta
