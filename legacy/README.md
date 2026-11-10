# GymProgress v1.0 (legado)

Aplicación de escritorio en Java + JavaFX + MySQL. Se conserva como referencia; **no se mantiene**.
La versión nueva vive en `backend/` y `frontend/`, y se construye a partir de `SPECS/`.

- Qué hacía y cómo estaba hecha: [`docs/as-is/sistema-actual.md`](../docs/as-is/sistema-actual.md)
- Por qué se reescribe: [`docs/as-is/hallazgos.md`](../docs/as-is/hallazgos.md)
- Estado exacto de esta versión en el historial: etiqueta `v1.0`

## Ejecutarla

Desde esta carpeta, con JDK 17+, MySQL 8 y conexión a internet:

1. `mysql -u root -p < gymprogress.sql`
2. Escribir usuario y contraseña de MySQL en `app/src/main/java/org/gymprogress/dao/ConexionDB.java`. No subir ese cambio.
3. `gradlew.bat run` (Windows) o `./gradlew run` (Linux / macOS)
