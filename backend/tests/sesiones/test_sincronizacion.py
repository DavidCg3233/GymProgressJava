"""Lo registrado sin conexión no se pierde al sincronizar tarde (T-006-19, T-006-20).

Spec 006 · RF-006-16, RF-006-17 · RN-006-12 · RNF-006-06.

Cada acción lleva `momento`: la hora en que ocurrió en el celular. El servidor
decide con esa hora, no con la hora en que le llega: una serie confirmada
dentro de la sesión se acepta aunque se sincronice horas después.
"""

from datetime import timedelta

import pytest

from .conftest import nuevo_id

pytestmark = pytest.mark.django_db


def detalle(api, sesion):
    return api.get(f"/api/sesiones/{sesion}/").json()["sesion"]


def test_series_confirmadas_sin_senal_se_aceptan_aunque_lleguen_3_horas_despues(api, reloj, ahora):
    # Empecé con señal; la perdí; confirmé 3 series; volví a tener señal 3 horas después.
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)

    reloj.avanzar(hours=3)

    for numero in (1, 2, 3):
        api.serie(ejercicio, numero=numero, momento=ahora + timedelta(minutes=10 * numero))
    respuesta = api.terminar(sesion, ahora, fin=ahora + timedelta(hours=2))

    assert respuesta.status_code == 200
    assert len(respuesta.json()["sesion"]["ejercicios"][0]["series"]) == 3
    assert [s["id"] for s in api.get("/api/sesiones/").json()["sesiones"]] == [sesion]


def test_una_sesion_entera_hecha_sin_senal_se_sincroniza_al_dia_siguiente(api, ahora):
    # RF-006-17: empezar y terminar sin conexión.
    inicio = ahora - timedelta(days=1)
    sesion = api.sesion(inicio=inicio)
    ejercicio = api.ejercicio(sesion, momento=inicio + timedelta(minutes=1))
    api.serie(ejercicio, numero=1, peso=30, reps=10, momento=inicio + timedelta(minutes=5))

    respuesta = api.terminar(sesion, inicio, fin=inicio + timedelta(minutes=50), nota="sin señal en el gimnasio")

    terminada = respuesta.json()["sesion"]
    assert terminada["fin"] == (inicio + timedelta(minutes=50)).isoformat()
    assert terminada["nota"] == "sin señal en el gimnasio"
    assert terminada["ejercicios"][0]["series"][0]["peso"] == 30.0


def test_una_accion_hecha_despues_del_cierre_automatico_se_rechaza(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)
    api.serie(ejercicio, numero=1)

    reloj.avanzar(hours=3)

    respuesta = api.put(
        f"/api/series/{nuevo_id()}/",
        ejercicio=ejercicio,
        numero=2,
        peso=30,
        reps=10,
        confirmada=True,
        momento=(ahora + timedelta(hours=2, minutes=1)).isoformat(),
    )
    assert respuesta.status_code == 409


def test_el_cierre_que_envia_el_celular_reemplaza_al_cierre_automatico_del_servidor(api, reloj, ahora):
    # El servidor cerró la sesión por su cuenta a las 2 horas; después llega
    # el cierre real del celular, con su nota y su hora.
    sesion = api.sesion(inicio=ahora)
    api.serie(api.ejercicio(sesion))
    reloj.avanzar(hours=5)
    assert detalle(api, sesion)["en_curso"] is False

    respuesta = api.terminar(sesion, ahora, fin=ahora + timedelta(minutes=70), nombre="Pecho en casa", nota="rápida")

    terminada = respuesta.json()["sesion"]
    assert terminada["fin"] == (ahora + timedelta(minutes=70)).isoformat()
    assert terminada["nombre"] == "Pecho en casa"
    assert terminada["nota"] == "rápida"


def test_una_sesion_vencida_y_vacia_no_se_borra_enseguida_por_si_faltan_series_por_llegar(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)

    reloj.avanzar(hours=3)
    assert api.get(f"/api/sesiones/{sesion}/").status_code == 404  # no se muestra...

    api.serie(ejercicio, numero=1, momento=ahora + timedelta(minutes=20))  # ...pero aún recibe lo pendiente

    assert len(detalle(api, sesion)["ejercicios"][0]["series"]) == 1


def test_una_sesion_vencida_y_vacia_se_borra_definitivamente_al_dia_siguiente(api, reloj, ahora):
    sesion = api.sesion(inicio=ahora)
    ejercicio = api.ejercicio(sesion)

    reloj.avanzar(hours=27)
    api.get("/api/sesiones/")  # cualquier consulta hace la limpieza

    respuesta = api.put(
        f"/api/series/{nuevo_id()}/",
        ejercicio=ejercicio,
        numero=1,
        peso=30,
        reps=10,
        confirmada=True,
        momento=(ahora + timedelta(minutes=20)).isoformat(),
    )
    assert respuesta.status_code == 404


def test_el_momento_debe_ser_una_hora_valida(api, ahora):
    sesion = api.sesion(inicio=ahora)

    respuesta = api.put(
        f"/api/series/{nuevo_id()}/",
        ejercicio=api.ejercicio(sesion),
        numero=1,
        peso=30,
        reps=10,
        confirmada=True,
        momento="hace un rato",
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == "momento"
