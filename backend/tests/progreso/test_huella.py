"""La huella de los datos detecta lo agregado, lo quitado y lo cambiado (T-008-15)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from progreso.management.commands.huella_de_datos import comparar, huella
from sesiones.models import Serie

pytestmark = pytest.mark.django_db

HACE_UN_RATO = datetime(2026, 11, 9, 18, tzinfo=ZoneInfo("America/Bogota"))


def test_sin_cambios_no_reporta_nada(api):
    api.sesion_terminada([(30, 10)], inicio=HACE_UN_RATO)
    antes = huella()

    informe = comparar(antes, huella())

    assert all(not t["agregadas"] and not t["quitadas"] and not t["cambiadas"] for t in informe.values())


def test_detecta_una_serie_cambiada_quitada_y_una_sesion_nueva(api):
    api.sesion_terminada([(30, 10), (32.5, 8)], inicio=HACE_UN_RATO)
    antes = huella()
    primera, segunda = Serie.objects.order_by("numero")
    id_segunda = str(segunda.pk)  # después de delete() Django le borra el pk
    primera.reps = 9
    primera.save()
    segunda.delete()
    api.sesion_terminada([(40, 5)], inicio=HACE_UN_RATO.replace(day=10))

    informe = comparar(antes, huella())

    assert informe["series"]["cambiadas"] == [str(primera.pk)]
    assert informe["series"]["quitadas"] == [id_segunda]
    assert len(informe["sesiones"]["agregadas"]) == 1
