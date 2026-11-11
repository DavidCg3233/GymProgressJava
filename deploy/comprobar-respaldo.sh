#!/usr/bin/env bash
# Comprueba que un respaldo se puede restaurar en limpio (T-006-35 · RNF-MAN-06).
#
# Uso: GP_RESPALDO_CLAVE=... GP_PRUEBA_DB_URL=... deploy/comprobar-respaldo.sh archivo.dump.gpg
#
# Descifra, restaura en una base vacía (nunca en la de producción) y cuenta las
# filas de las tablas principales. Falla si no se puede descifrar, si la
# restauración da error o si no hay ninguna cuenta.
set -euo pipefail

entrada="${1:?Falta el archivo del respaldo}"
: "${GP_RESPALDO_CLAVE:?Falta GP_RESPALDO_CLAVE}"
: "${GP_PRUEBA_DB_URL:?Falta GP_PRUEBA_DB_URL}"

gpg --batch --quiet --pinentry-mode loopback --passphrase-fd 3 --decrypt "$entrada" \
  3< <(printf '%s' "$GP_RESPALDO_CLAVE") |
  docker run --rm -i --network host -e GP_PRUEBA_DB_URL postgres:18-alpine \
    sh -c 'pg_restore --no-owner --no-privileges --exit-on-error --dbname "$GP_PRUEBA_DB_URL"'

consulta="SELECT 'cuentas', count(*) FROM cuentas_usuario
UNION ALL SELECT 'sesiones', count(*) FROM sesiones_sesion
UNION ALL SELECT 'series', count(*) FROM sesiones_serie
UNION ALL SELECT 'rutinas', count(*) FROM rutinas_rutina
UNION ALL SELECT 'pesos', count(*) FROM cuerpo_registrodepeso;"

conteo=$(docker run --rm --network host -e GP_PRUEBA_DB_URL postgres:18-alpine \
  psql "$GP_PRUEBA_DB_URL" --tuples-only --no-align --field-separator=' ' --command "$consulta")

echo "Restaurado en limpio. Filas por tabla:"
echo "$conteo"

cuentas=$(echo "$conteo" | awk '$1 == "cuentas" { print $2 }')
if [ "${cuentas:-0}" -lt 1 ]; then
  echo "::error title=Respaldo vacío::El respaldo se restauró pero no tiene ninguna cuenta."
  exit 1
fi
