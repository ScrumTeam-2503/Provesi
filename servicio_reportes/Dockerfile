FROM python:3.10-slim

WORKDIR /app

# Copiar archivos de la aplicación
COPY requirements.txt .
COPY main.py .
COPY models.py .
COPY database.py .
COPY pdf_generator.py .

# Variables de entorno con defaults genéricos
# Las IPs reales se inyectan en runtime con -e flags
# PostgreSQL
ENV DATABASE_HOST=localhost
ENV DATABASE_NAME=provesi_db
ENV DATABASE_USER=provesi_user
ENV DATABASE_PASSWORD=scrumteam
ENV DATABASE_PORT=5432

# MongoDB
ENV MONGODB_HOST=localhost
ENV MONGODB_PORT=27017
ENV MONGODB_DATABASE=provesi_mongodb
ENV MONGODB_USER=provesi_user
ENV MONGODB_PASSWORD=scrumteam
ENV MONGODB_AUTH_SOURCE=provesi_mongodb

# Instalar dependencias
RUN apt-get update \
    && apt-get install -y gcc libpq-dev python3-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

