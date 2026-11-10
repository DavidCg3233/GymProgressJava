"""La base de datos real es PostgreSQL 16 (plan 006, sección 2 · T-006-03).

Estas pruebas solo corren dentro de Docker Compose, donde GP_DB_HOST está
definida. En el equipo, con SQLite, se omiten.
"""

import pytest
from django.db import connection

pytestmark = [pytest.mark.postgres, pytest.mark.django_db]


def test_el_servidor_esta_conectado_a_postgresql():
    assert connection.vendor == "postgresql"


def test_la_version_de_postgresql_es_la_del_plan():
    version_mayor = connection.pg_version // 10000

    assert version_mayor == 16


def test_las_migraciones_iniciales_estan_aplicadas():
    # Si la tabla de cuentas existe, las migraciones corrieron (RNF-MAN-02).
    assert "cuentas_usuario" in connection.introspection.table_names()
