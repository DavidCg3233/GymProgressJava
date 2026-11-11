#!/usr/bin/env bash
# Respaldo de la base de producción, cifrado (T-006-35 · RNF-MAN-06).
#
# Uso: GP_RESPALDO_DB_URL=... GP_RESPALDO_CLAVE=... deploy/respaldo.sh archivo-de-salida.dump.gpg
#
# - El volcado sale en formato "custom" de PostgreSQL: se restaura con pg_restore.
# - Se cifra con AES-256 y la clave de GP_RESPALDO_CLAVE. Sin esa clave, el archivo no sirve.
# - El volcado sin cifrar nunca queda en disco: pasa directo de pg_dump a gpg.
# - Ni la dirección de la base ni la clave se escriben en los registros (RNF-SEG-08).
set -euo pipefail

salida="${1:?Falta el nombre del archivo de salida}"
: "${GP_RESPALDO_DB_URL:?Falta GP_RESPALDO_DB_URL}"
: "${GP_RESPALDO_CLAVE:?Falta GP_RESPALDO_CLAVE}"

# pg_dump de PostgreSQL 18: un cliente más nuevo puede volcar servidores más viejos.
# La clave le llega a gpg por un descriptor de archivo, no como argumento: así no
# aparece en la lista de procesos.
docker run --rm --network host -e GP_RESPALDO_DB_URL postgres:18-alpine \
  sh -c 'pg_dump "$GP_RESPALDO_DB_URL" --format=custom --no-owner --no-privileges' |
  gpg --batch --yes --quiet --pinentry-mode loopback \
    --passphrase-fd 3 --symmetric --cipher-algo AES256 --output "$salida" \
    3< <(printf '%s' "$GP_RESPALDO_CLAVE")

echo "Respaldo cifrado: $salida ($(du -h "$salida" | cut -f1))"
