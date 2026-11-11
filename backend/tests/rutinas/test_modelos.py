"""La base de datos defiende el catálogo y las rutinas por sí sola (T-002-03).

Estas pruebas escriben directo en la base, saltándose los servicios, para
comprobar que las restricciones existen aunque el código tuviera un error.
Spec 002 · RN-002-01 a 08 · RF-002-06, 16, 19 · plan 002, sección 4.1.
"""

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import RestrictedError
from django.utils import timezone

from rutinas.models import Ejercicio, GrupoMuscular, Rutina, RutinaEjercicio
from sesiones.models import Sesion, SesionEjercicio

from .conftest import crear_cuenta

pytestmark = pytest.mark.django_db


def nuevo(modelo, **datos):
    return modelo.objects.create(id=uuid.uuid4(), **datos)


@pytest.fixture
def david(db):
    usuario = crear_cuenta()
    # Partir de un catálogo vacío: el predefinido se prueba aparte.
    Ejercicio.objects.filter(usuario=usuario).delete()
    GrupoMuscular.objects.filter(usuario=usuario).delete()
    return usuario


@pytest.fixture
def pecho(david):
    return nuevo(GrupoMuscular, usuario=david, nombre="Pecho")


@pytest.fixture
def press(david, pecho):
    return nuevo(Ejercicio, usuario=david, nombre="Press inclinado", grupo=pecho)


@pytest.fixture
def rutina(david):
    return nuevo(Rutina, usuario=david, nombre="Pecho", dias=0)


def fila(rutina, ejercicio, **cambios):
    datos = {"orden": 1, "series": 3, "reps": 10, "peso": Decimal("30")} | cambios
    return RutinaEjercicio.objects.create(rutina=rutina, ejercicio=ejercicio, **datos)


# --- La clave se calcula sola -----------------------------------------------


def test_la_clave_es_el_nombre_sin_mayusculas_ni_tildes(david, pecho):
    ejercicio = nuevo(Ejercicio, usuario=david, nombre="  Préss INCLINADO ", grupo=pecho)

    assert ejercicio.nombre == "Préss INCLINADO"
    assert ejercicio.clave == "press inclinado"


# --- Unicidad ---------------------------------------------------------------


def test_un_grupo_no_se_repite_en_el_catalogo_de_una_persona(david, pecho):
    with pytest.raises(IntegrityError), transaction.atomic():
        nuevo(GrupoMuscular, usuario=david, nombre="PECHO")


def test_un_ejercicio_no_se_repite_aunque_cambien_mayusculas_o_tildes(david, pecho, press):
    with pytest.raises(IntegrityError), transaction.atomic():
        nuevo(Ejercicio, usuario=david, nombre="préss inclinado", grupo=pecho)


def test_una_rutina_no_repite_nombre(david, rutina):
    with pytest.raises(IntegrityError), transaction.atomic():
        nuevo(Rutina, usuario=david, nombre="pecho", dias=0)


def test_dos_personas_si_pueden_tener_el_mismo_nombre(david, pecho, press, rutina):
    andrea = crear_cuenta("andrea")

    grupo = GrupoMuscular.objects.get(usuario=andrea, clave="pecho")  # viene del catálogo inicial
    nuevo(Rutina, usuario=andrea, nombre="Pecho", dias=0)

    assert grupo.pk != pecho.pk


def test_un_ejercicio_aparece_una_sola_vez_por_rutina(rutina, press):
    fila(rutina, press)

    with pytest.raises(IntegrityError), transaction.atomic():
        fila(rutina, press, orden=2)


# --- Rangos -----------------------------------------------------------------


@pytest.mark.parametrize(
    "cambios",
    [
        pytest.param({"series": 0}, id="cero series"),
        pytest.param({"series": 11}, id="once series"),
        pytest.param({"reps": 0}, id="cero reps"),
        pytest.param({"reps": 101}, id="ciento una reps"),
        pytest.param({"peso": Decimal("-0.5")}, id="peso negativo"),
        pytest.param({"peso": Decimal("500.5")}, id="peso sobre el maximo"),
    ],
)
def test_la_base_rechaza_lo_previsto_fuera_de_rango(rutina, press, cambios):
    with pytest.raises(IntegrityError), transaction.atomic():
        fila(rutina, press, **cambios)


@pytest.mark.parametrize("dias", [-1, 128])
def test_la_base_rechaza_dias_fuera_de_rango(david, dias):
    with pytest.raises(IntegrityError), transaction.atomic():
        nuevo(Rutina, usuario=david, nombre="Rara", dias=dias)


# --- Borrados ---------------------------------------------------------------


def test_ca_002_19a_un_grupo_con_ejercicios_no_se_puede_borrar(pecho, press):
    with pytest.raises(RestrictedError):
        pecho.delete()


def test_un_grupo_sin_ejercicios_si_se_puede_borrar(pecho):
    pecho.delete()

    assert GrupoMuscular.objects.count() == 0


def test_borrar_un_ejercicio_lo_quita_de_las_rutinas(rutina, press):
    fila(rutina, press)

    press.delete()

    assert RutinaEjercicio.objects.count() == 0
    assert Rutina.objects.filter(pk=rutina.pk).exists()


def test_borrar_una_rutina_borra_sus_ejercicios_previstos_pero_no_los_del_catalogo(rutina, press):
    fila(rutina, press)

    rutina.delete()

    assert RutinaEjercicio.objects.count() == 0
    assert Ejercicio.objects.filter(pk=press.pk).exists()


def test_rf_002_06_borrar_una_rutina_no_toca_sus_sesiones(david, rutina, press):
    inicio = timezone.now() - timedelta(days=1)
    sesion = nuevo(Sesion, usuario=david, nombre="Pecho", inicio=inicio, fin=inicio + timedelta(hours=1), rutina=rutina)
    hecho = nuevo(
        SesionEjercicio, sesion=sesion, nombre="Press inclinado", clave="press inclinado", grupo="Pecho", orden=1, ejercicio=press
    )

    rutina.delete()
    press.delete()

    sesion.refresh_from_db()
    hecho.refresh_from_db()
    assert sesion.rutina is None
    assert sesion.nombre == "Pecho"
    assert hecho.ejercicio is None
    assert (hecho.nombre, hecho.grupo) == ("Press inclinado", "Pecho")


def test_borrar_la_cuenta_borra_su_catalogo_y_sus_rutinas(david, press, rutina):
    david.delete()

    assert (GrupoMuscular.objects.count(), Ejercicio.objects.count(), Rutina.objects.count()) == (0, 0, 0)
