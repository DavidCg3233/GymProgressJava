# Imagen del servidor de GymProgress.
# La versión de Python es la del plan 006; no usar "latest" (RNF-SEG-07).
FROM python:3.12-slim

# Sin archivos .pyc y con la salida directa a los registros del contenedor.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Qué dependencias instalar: producción por defecto; desarrollo y pruebas
# pasan REQUISITOS=requirements-dev.txt desde docker-compose.
ARG REQUISITOS=requirements.txt

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r ${REQUISITOS}

# El servidor no corre como administrador dentro del contenedor.
RUN useradd --create-home --uid 1000 gymprogress
USER gymprogress

COPY --chown=gymprogress:gymprogress . .

EXPOSE 8000
