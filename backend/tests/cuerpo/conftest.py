"""Las pruebas del cuerpo usan las mismas herramientas que las de sesiones:
una API con acceso, una segunda cuenta, un reloj que se puede adelantar.
"""

from tests.sesiones.conftest import (  # noqa: F401 (fixtures que pytest descubre por nombre)
    BACKEND,
    CONTRASENA,
    Api,
    ahora,
    anonimo,
    api,
    crear_cuenta,
    cuenta,
    nuevo_id,
    otra,
    reloj,
)
