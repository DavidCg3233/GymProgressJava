"""Una sesión se vuelve rutina (T-008-02).

Spec 008 · RN-008-05, 06, 07 · CA-008-06a, 07a · plan 008, sección 4.1.
"""

from decimal import Decimal

import pytest

from reglas.errores import ErrorDeValidacion
from reglas.progreso import SerieHecha
from reglas.sesion_a_rutina import Cambio, Previsto, actualizar_rutina, ejercicios_de_sesion, rutina_nueva

D = Decimal


def ejercicio(nombre, grupo, *series):
    """Un ejercicio de la sesión con sus series confirmadas: (peso, reps)."""
    return {
        "clave": nombre.lower(),
        "nombre": nombre,
        "grupo": grupo,
        "series": [SerieHecha(D(str(peso)), reps, numero) for numero, (peso, reps) in enumerate(series, start=1)],
    }


def previsto(nombre, grupo, series, peso, reps):
    return Previsto(clave=nombre.lower(), nombre=nombre, grupo=grupo, series=series, peso=D(str(peso)), reps=reps)


SESION_CA_06A = [
    ejercicio("Sentadilla", "Pierna", (60, 8), (70, 6), (70, 5)),
    ejercicio("Prensa", "Pierna", (120, 10), (120, 10)),
]


# --- Ejercicios de una sesión (RN-008-05) ------------------------------------


def test_ca_008_06a_series_confirmadas_y_mejor_serie_en_el_orden_de_la_sesion():
    assert ejercicios_de_sesion(SESION_CA_06A) == [
        previsto("Sentadilla", "Pierna", 3, 70, 6),
        previsto("Prensa", "Pierna", 2, 120, 10),
    ]


def test_un_ejercicio_sin_series_confirmadas_no_entra():
    assert ejercicios_de_sesion([ejercicio("Fondos", "Pecho"), *SESION_CA_06A])[0].nombre == "Sentadilla"


def test_el_mismo_ejercicio_dos_veces_queda_una_vez_con_sus_series_sumadas():
    sesion = [
        ejercicio("Sentadilla", "Pierna", (60, 8), (60, 8)),
        ejercicio("Prensa", "Pierna", (120, 10)),
        ejercicio("Sentadilla", "Pierna", (75, 3)),
    ]

    assert ejercicios_de_sesion(sesion) == [
        previsto("Sentadilla", "Pierna", 3, 75, 3),
        previsto("Prensa", "Pierna", 1, 120, 10),
    ]


def test_las_series_previstas_no_pasan_de_10():
    sesion = [
        ejercicio("Plancha", "Abdomen", *[(0, 30)] * 6),
        ejercicio("Plancha", "Abdomen", *[(0, 40)] * 5),
    ]

    assert ejercicios_de_sesion(sesion)[0].series == 10


# --- Rutina nueva (RN-008-06) ------------------------------------------------


def test_rutina_nueva_con_los_ejercicios_de_la_sesion():
    assert rutina_nueva(ejercicios_de_sesion(SESION_CA_06A)) == ejercicios_de_sesion(SESION_CA_06A)


def test_una_sesion_sin_series_confirmadas_no_hace_rutina():
    with pytest.raises(ErrorDeValidacion) as error:
        rutina_nueva([])

    assert (error.value.campo, error.value.mensaje) == (
        "ejercicios",
        "Esta sesión no tiene series confirmadas: no hay nada que guardar como rutina.",
    )


def test_21_ejercicios_se_rechazan_diciendo_cuantos_sobran():
    muchos = [previsto(f"Ejercicio {n}", "Pecho", 3, 10, 10) for n in range(21)]

    with pytest.raises(ErrorDeValidacion) as error:
        rutina_nueva(muchos)

    assert error.value.mensaje == "Una rutina admite máximo 20 ejercicios: esta tiene 21, sobra 1."


# --- Actualizar una rutina (RN-008-07) ---------------------------------------

PIERNA = [
    previsto("Sentadilla", "Pierna", 3, 65, 6),
    previsto("Curl femoral", "Pierna", 3, 30, 12),
]


def test_ca_008_07a_suma_mejora_y_no_quita():
    sesion = ejercicios_de_sesion(
        [
            ejercicio("Sentadilla", "Pierna", (70, 6), (65, 6)),
            ejercicio("Prensa", "Pierna", (120, 10), (110, 10)),
        ]
    )

    nuevos, cambios = actualizar_rutina(PIERNA, sesion)

    assert nuevos == [
        previsto("Sentadilla", "Pierna", 3, 70, 6),
        previsto("Curl femoral", "Pierna", 3, 30, 12),
        previsto("Prensa", "Pierna", 2, 120, 10),
    ]
    assert cambios == [
        Cambio("mejora", "Sentadilla", antes=(D("65"), 6), despues=(D("70"), 6)),
        Cambio("igual", "Curl femoral", antes=(D("30"), 12), despues=(D("30"), 12)),
        Cambio("agrega", "Prensa", antes=None, despues=(D("120"), 10)),
    ]


def test_una_sesion_que_no_supera_deja_lo_previsto():
    sesion = ejercicios_de_sesion([ejercicio("Sentadilla", "Pierna", (60, 10))])

    nuevos, cambios = actualizar_rutina(PIERNA, sesion)

    assert nuevos == PIERNA
    assert [cambio.tipo for cambio in cambios] == ["igual", "igual"]


def test_mejorar_no_cambia_las_series_previstas():
    sesion = ejercicios_de_sesion([ejercicio("Sentadilla", "Pierna", (80, 5))])

    nuevos, _ = actualizar_rutina(PIERNA, sesion)

    assert nuevos[0].series == 3


def test_actualizar_que_pase_de_20_se_rechaza():
    rutina = [previsto(f"Ejercicio {n}", "Pecho", 3, 10, 10) for n in range(19)]
    sesion = ejercicios_de_sesion([ejercicio("Nuevo A", "Pecho", (10, 10)), ejercicio("Nuevo B", "Pecho", (10, 10))])

    with pytest.raises(ErrorDeValidacion) as error:
        actualizar_rutina(rutina, sesion)

    assert error.value.mensaje == "Una rutina admite máximo 20 ejercicios: quedaría con 21, sobra 1."
