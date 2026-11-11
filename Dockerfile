# Imagen de producción de GymProgress (la usa Railway).
#
# Dos etapas: primero se compila la pantalla con Node; luego se arma el
# servidor con Python y se le copia la pantalla ya compilada. Node no llega a
# la imagen final: solo lo que hace falta para correr.
#
# Para desarrollo en tu equipo se usa deploy/docker-compose.yml, no este archivo.

# --- Etapa 1: compilar la pantalla ---------------------------------------
FROM node:22-alpine AS pantalla
WORKDIR /pantalla
# Primero solo las dependencias: si no cambian, Docker reutiliza esta capa.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-fund --no-audit
COPY frontend/ ./
RUN npm run build

# --- Etapa 2: el servidor ------------------------------------------------
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GP_PANTALLA_DIR=/app/pantalla

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# El servidor no corre como administrador dentro del contenedor. La carpeta /app
# la creó el administrador: se le entrega al usuario para que pueda escribir en
# ella (collectstatic crea /app/staticfiles).
RUN useradd --create-home --uid 1000 gymprogress     && chown gymprogress:gymprogress /app
COPY --chown=gymprogress:gymprogress backend/ ./
COPY --from=pantalla --chown=gymprogress:gymprogress /pantalla/dist /app/pantalla
USER gymprogress

# Reúne los archivos del panel. La configuración exige variables de entorno para
# arrancar; aquí se dan valores de mentira que solo existen durante este paso.
RUN GP_SECRET_KEY=solo-para-compilar GP_DB_NAME=x GP_DB_USER=x GP_DB_PASSWORD=x GP_DB_HOST=x \
    python manage.py collectstatic --noinput

# Railway indica el puerto en PORT. Antes de atender, aplica las migraciones
# pendientes (RNF-MAN-02). Un proceso con 4 hilos: suficiente para 5 cuentas y
# usa menos memoria (lo que Railway cobra) que varios procesos.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --worker-class gthread --timeout 30 --access-logfile -"]
