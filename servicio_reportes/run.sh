#!/bin/bash

# Script para ejecutar el servicio de reportes

echo "🚀 Iniciando Servicio de Reportes - Provesi WMS"
echo "================================================"

# Verificar si existe un entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar/actualizar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar variables de entorno
if [ ! -f ".env" ]; then
    echo "⚠️  No se encontró archivo .env, usando valores por defecto"
    echo "💡 Copia .env.example a .env y configura tus variables"
fi

# Ejecutar el servicio
echo "✅ Iniciando servidor FastAPI..."
echo "📖 Documentación disponible en: http://localhost:8000/docs"
echo "================================================"

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

