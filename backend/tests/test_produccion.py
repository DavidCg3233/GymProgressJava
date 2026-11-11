"""Lo que cambia al publicar la app (plan 006, sección 2 revisada: Railway).

- RNF-SEG-02: todo por HTTPS cuando la app está publicada.
- RNF-SEG-05: la página solo ejecuta código propio (Content-Security-Policy).
- Un solo sitio: Django entrega la API y también la pantalla, así la cookie de
  acceso y la protección CSRF funcionan igual que en desarrollo.
"""

import pytest
from django.test import override_settings

from config.produccion import ajustes_https, politica_de_contenido

# --- HTTPS (RNF-SEG-02) -----------------------------------------------------


def test_publicada_todo_se_redirige_a_https_y_se_avisa_al_navegador_por_un_anio():
    ajustes = ajustes_https(activo=True)

    assert ajustes["SECURE_SSL_REDIRECT"] is True
    assert ajustes["SECURE_HSTS_SECONDS"] == 365 * 24 * 60 * 60
    assert ajustes["SESSION_COOKIE_SECURE"] is True
    assert ajustes["CSRF_COOKIE_SECURE"] is True


def test_publicada_confia_en_que_el_proxy_de_railway_indique_si_la_peticion_llego_por_https():
    # Railway recibe el HTTPS y le pasa la petición a Django por HTTP interno.
    assert ajustes_https(activo=True)["SECURE_PROXY_SSL_HEADER"] == ("HTTP_X_FORWARDED_PROTO", "https")


def test_la_revision_de_salud_de_railway_no_se_redirige():
    # Railway pregunta por /salud/ desde adentro, por HTTP: una redirección la haría fallar.
    assert ajustes_https(activo=True)["SECURE_REDIRECT_EXEMPT"] == [r"^salud/$"]


def test_en_el_equipo_no_se_exige_https():
    ajustes = ajustes_https(activo=False)

    assert ajustes["SECURE_SSL_REDIRECT"] is False
    assert ajustes["SECURE_HSTS_SECONDS"] == 0
    assert "SECURE_PROXY_SSL_HEADER" not in ajustes


# --- Content-Security-Policy (RNF-SEG-05) -----------------------------------


def test_la_politica_solo_permite_recursos_del_mismo_sitio():
    politica = politica_de_contenido()

    assert "default-src 'self'" in politica
    assert "script-src 'self'" in politica
    assert "object-src 'none'" in politica
    assert "frame-ancestors 'none'" in politica
    assert "unsafe-eval" not in politica


@pytest.mark.parametrize("ruta", ["/salud/", "/api/acceso/"])
def test_las_respuestas_llevan_la_politica_de_contenido(client, db, ruta):
    respuesta = client.get(ruta)

    assert respuesta["Content-Security-Policy"] == politica_de_contenido()


def test_el_panel_del_dueno_no_lleva_la_politica_porque_usa_codigo_propio_de_django(client, db):
    respuesta = client.get("/panel/login/")

    assert "Content-Security-Policy" not in respuesta


# --- La pantalla servida por Django -----------------------------------------


@pytest.fixture
def pantalla_compilada(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>GymProgress</title>", encoding="utf-8")
    with override_settings(PANTALLA_DIR=tmp_path):
        yield tmp_path


def test_la_raiz_entrega_la_pantalla(client, pantalla_compilada):
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert b"<title>GymProgress</title>" in respuesta.content
    assert respuesta["Content-Type"].startswith("text/html")


def test_la_pantalla_nunca_se_guarda_en_cache_para_que_las_actualizaciones_lleguen(client, pantalla_compilada):
    respuesta = client.get("/")

    assert "no-cache" in respuesta["Cache-Control"]


def test_la_pantalla_lleva_la_politica_de_contenido(client, pantalla_compilada):
    assert client.get("/")["Content-Security-Policy"] == politica_de_contenido()


def test_sin_la_pantalla_compilada_se_explica_el_problema_sin_romper(client, tmp_path):
    with override_settings(PANTALLA_DIR=tmp_path / "no-existe"):
        respuesta = client.get("/")

    assert respuesta.status_code == 503
    assert "pantalla" in respuesta.content.decode()


def test_una_ruta_de_la_api_que_no_existe_no_devuelve_la_pantalla(client, pantalla_compilada):
    assert client.get("/api/no-existe/").status_code == 404


# --- Archivos de la app entregados por WhiteNoise ---------------------------


@pytest.fixture
def archivos_de_la_app(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>GymProgress</title>", encoding="utf-8")
    (tmp_path / "sw.js").write_text("// service worker", encoding="utf-8")
    (tmp_path / "manifest.webmanifest").write_text('{"name": "GymProgress"}', encoding="utf-8")
    with override_settings(WHITENOISE_ROOT=tmp_path, PANTALLA_DIR=tmp_path):
        yield tmp_path


@pytest.mark.parametrize("ruta", ["/index.html", "/sw.js", "/manifest.webmanifest"])
def test_los_archivos_de_la_app_tambien_llevan_la_politica_de_contenido(client, archivos_de_la_app, ruta):
    # El service worker guarda /index.html y lo muestra sin señal: sin esta cabecera,
    # en el celular la app correría siempre sin la protección.
    respuesta = client.get(ruta)

    assert respuesta.status_code == 200
    assert respuesta["Content-Security-Policy"] == politica_de_contenido()


def test_el_manifiesto_se_entrega_con_su_tipo_para_que_la_app_se_pueda_instalar(client, archivos_de_la_app):
    assert client.get("/manifest.webmanifest")["Content-Type"].startswith("application/manifest+json")
