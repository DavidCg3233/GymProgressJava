# Respaldo diario (T-006-35 · RNF-MAN-06)

Cada madrugada (3:00 a. m. de Colombia), GitHub Actions corre [`respaldo.yml`](../.github/workflows/respaldo.yml). El flujo hace cuatro cosas:

1. **Vuelca** la base de producción de Railway con `pg_dump`.
2. **La cifra** con AES-256 y una clave que solo tienes tú. El volcado sin cifrar nunca queda en disco.
3. **Comprueba que se restaura en limpio** en una base vacía y cuenta cuentas, sesiones, series, rutinas y pesos. Si no se puede restaurar, el respaldo falla y GitHub te avisa por correo.
4. **Guarda el archivo cifrado 30 días** como archivo de esa ejecución, en la pestaña **Actions** del repositorio.

Además, cada PR prueba los mismos scripts con la base de la revisión automática. Así un cambio no rompe el respaldo sin que se note.

## Configurarlo (una sola vez)

En GitHub: **Settings → Secrets and variables → Actions → New repository secret**.

| Secreto | Qué poner | De dónde sale |
|---|---|---|
| `GP_RESPALDO_DB_URL` | La dirección pública de la base | Railway → servicio **Postgres** → **Variables** → `DATABASE_PUBLIC_URL` |
| `GP_RESPALDO_CLAVE` | Una frase larga que inventes (20 o más caracteres) | Tú. **Guárdala en tu gestor de contraseñas: sin ella, ningún respaldo se puede abrir.** |

Después, en **Actions → Respaldo diario → Run workflow**, córrelo una vez a mano y revisa que salga en verde.

> El repositorio es público: cualquiera con cuenta de GitHub puede descargar el archivo. Por eso va cifrado, y por eso la clave nunca entra al repositorio.

## Restaurar una copia

Hazlo en tu máquina virtual de Linux: ya tiene todo lo necesario y es práctica de tu rama de Linux.

1. **Descargar.** En GitHub, **Actions → Respaldo diario**, elige la ejecución del día que quieres y descarga el archivo `gymprogress-AAAA-MM-DD.dump.gpg` (viene dentro de un `.zip`).
2. **Instalar las herramientas** (una vez):

   ```bash
   sudo apt install gnupg postgresql-client
   ```

3. **Descifrar.** Te pide la clave de `GP_RESPALDO_CLAVE`:

   ```bash
   gpg --output gymprogress.dump --decrypt gymprogress-AAAA-MM-DD.dump.gpg
   ```

4. **Ver qué trae, sin tocar nada:**

   ```bash
   pg_restore --list gymprogress.dump | head -30
   ```

5. **Probar en una base vacía tuya** (la prueba de T-006-35):

   ```bash
   createdb gymprogress_prueba
   pg_restore --no-owner --no-privileges --dbname gymprogress_prueba gymprogress.dump
   psql gymprogress_prueba -c "SELECT count(*) FROM sesiones_sesion;"
   ```

6. **Solo en un desastre real, restaurar sobre producción.** Esto **reemplaza** los datos actuales por los del respaldo, y lo que se registró después de esa fecha se pierde:

   ```bash
   pg_restore --clean --if-exists --no-owner --no-privileges --dbname "DATABASE_PUBLIC_URL de Railway" gymprogress.dump
   ```

7. **Borrar el archivo descifrado** cuando termines: tiene tus datos de salud sin protección.

   ```bash
   shred -u gymprogress.dump
   ```
