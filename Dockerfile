# 1. Usamos una imagen ligera de Python 3.11
FROM python:3.11-slim

# 2. Evitamos que Python genere archivos .pyc y aseguramos que los logs se vean en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /code

# 4. Instalamos dependencias del sistema necesarias para PostgreSQL (libpq-dev y gcc)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 5. Copiamos el archivo de requisitos e instalamos las librerías de Python
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el código del proyecto al contenedor
COPY . /code/