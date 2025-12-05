# Servicio de Reportes - Provesi WMS

Microservicio desarrollado con FastAPI para generar reportes de inventario y pedidos del sistema WMS Provesi.

## 🚀 Características

- **Reportes de Inventario**: Estadísticas completas de productos, bodegas, estanterías y ubicaciones
- **Reportes de Pedidos**: Análisis de pedidos por estado, método de pago y fechas
- **Productos Más Vendidos**: Ranking de productos más solicitados
- **Capacidad de Bodegas**: Análisis de ocupación y disponibilidad
- **Ventas por Fecha**: Análisis temporal de ventas (por día, mes o año)
- **Integración MongoDB**: Consultas directas a la base de datos NoSQL

## 📋 Requisitos

- Python 3.10+
- PostgreSQL (conexión a la base de datos principal)
- MongoDB (conexión a la base de datos de sincronización)
- Docker (opcional, para contenedores)

## 🔧 Instalación

### Instalación Local

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar el servicio:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Instalación con Docker

1. Construir la imagen:
```bash
docker build -t servicio-reportes:latest .
```

2. Ejecutar el contenedor:
```bash
docker run -d \
  --name servicio-reportes \
  -p 8000:8000 \
  -e DATABASE_HOST=34.229.88.183 \
  -e MONGODB_HOST=localhost \
  servicio-reportes:latest
```

## 📚 Endpoints Disponibles

### Health Check
- `GET /` - Información básica del servicio
- `GET /health` - Verificación de estado y conexiones a bases de datos

### Reportes de Inventario
- `GET /reportes/inventario` - Reporte completo de inventario
  - Query params: `bodega_codigo` (opcional)

### Reportes de Pedidos
- `GET /reportes/pedidos` - Reporte de pedidos
  - Query params: `estado`, `fecha_inicio`, `fecha_fin` (opcionales)

### Productos Más Vendidos
- `GET /reportes/productos-mas-vendidos` - Top productos vendidos
  - Query params: `limite` (1-100), `fecha_inicio`, `fecha_fin` (opcionales)

### Capacidad de Bodegas
- `GET /reportes/bodegas-capacidad` - Análisis de capacidad y ocupación

### Ventas por Fecha
- `GET /reportes/ventas-por-fecha` - Ventas agrupadas temporalmente
  - Query params: `fecha_inicio`, `fecha_fin`, `agrupar_por` (dia/mes/año)

### Reportes MongoDB
- `GET /reportes/mongodb/pedidos` - Últimos pedidos desde MongoDB
  - Query params: `limite` (1-100)
- `GET /reportes/mongodb/productos` - Productos desde MongoDB
  - Query params: `limite` (1-100)

### Reportes en PDF
Todos los reportes principales están disponibles en formato PDF agregando `/pdf` a la ruta:

- `GET /reportes/inventario/pdf` - Reporte de inventario en PDF
  - Query params: `bodega_codigo` (opcional)
- `GET /reportes/pedidos/pdf` - Reporte de pedidos en PDF
  - Query params: `estado`, `fecha_inicio`, `fecha_fin` (opcionales)
- `GET /reportes/productos-mas-vendidos/pdf` - Top productos en PDF
  - Query params: `limite` (1-100), `fecha_inicio`, `fecha_fin` (opcionales)
- `GET /reportes/bodegas-capacidad/pdf` - Capacidad de bodegas en PDF
- `GET /reportes/ventas-por-fecha/pdf` - Ventas por fecha en PDF
  - Query params: `fecha_inicio`, `fecha_fin`, `agrupar_por` (dia/mes/año)

## 📖 Documentación Interactiva

Una vez ejecutado el servicio, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Variables de Entorno

### PostgreSQL
- `DATABASE_HOST`: Host de PostgreSQL (default: 34.229.88.183)
- `DATABASE_NAME`: Nombre de la base de datos (default: provesi_db)
- `DATABASE_USER`: Usuario de PostgreSQL (default: provesi_user)
- `DATABASE_PASSWORD`: Contraseña de PostgreSQL (default: scrumteam)
- `DATABASE_PORT`: Puerto de PostgreSQL (default: 5432)

### MongoDB
- `MONGODB_HOST`: Host de MongoDB (default: localhost)
- `MONGODB_PORT`: Puerto de MongoDB (default: 27017)
- `MONGODB_DATABASE`: Nombre de la base de datos (default: provesi_mongodb)
- `MONGODB_USER`: Usuario de MongoDB (default: provesi_user)
- `MONGODB_PASSWORD`: Contraseña de MongoDB (default: scrumteam)
- `MONGODB_AUTH_SOURCE`: Base de datos de autenticación (default: provesi_mongodb)

## 🧪 Ejemplos de Uso

### Obtener reporte de inventario
```bash
curl http://localhost:8000/reportes/inventario
```

### Obtener reporte de inventario de una bodega específica
```bash
curl "http://localhost:8000/reportes/inventario?bodega_codigo=BOG01"
```

### Obtener pedidos pendientes
```bash
curl "http://localhost:8000/reportes/pedidos?estado=pendiente"
```

### Obtener top 5 productos más vendidos
```bash
curl "http://localhost:8000/reportes/productos-mas-vendidos?limite=5"
```

### Obtener ventas por mes
```bash
curl "http://localhost:8000/reportes/ventas-por-fecha?agrupar_por=mes"
```

### Obtener ventas en un rango de fechas
```bash
curl "http://localhost:8000/reportes/ventas-por-fecha?fecha_inicio=2024-01-01&fecha_fin=2024-12-31&agrupar_por=dia"
```

### Descargar reporte de inventario en PDF
```bash
curl "http://localhost:8000/reportes/inventario/pdf" --output reporte_inventario.pdf
```

### Descargar reporte de productos más vendidos en PDF
```bash
curl "http://localhost:8000/reportes/productos-mas-vendidos/pdf?limite=10" --output top_productos.pdf
```

### Descargar reporte de ventas por mes en PDF
```bash
curl "http://localhost:8000/reportes/ventas-por-fecha/pdf?agrupar_por=mes" --output ventas_mensuales.pdf
```

## 🏗️ Arquitectura

El servicio está diseñado para ejecutarse de forma independiente en una máquina separada:

```
┌─────────────────────────────────────┐
│   Servicio de Reportes (FastAPI)   │
│                                     │
│  ┌──────────────────────────────┐  │
│  │       Endpoints REST         │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────┐    ┌──────────────┐  │
│  │  Models  │    │   Database   │  │
│  │ (Pydantic)│   │  Connections │  │
│  └──────────┘    └──────────────┘  │
└─────────────────────────────────────┘
           │              │
           │              │
     ┌─────▼─────┐   ┌───▼────────┐
     │ PostgreSQL │   │  MongoDB   │
     │  (Provesi) │   │  (Provesi) │
     └────────────┘   └────────────┘
```

## 🔄 Integración con Kong

Para integrar este servicio con Kong API Gateway, agregar la siguiente configuración:

```yaml
services:
  - name: servicio-reportes
    url: http://servicio-reportes:8000
    routes:
      - name: reportes-route
        paths:
          - /reportes
        strip_path: false
```

## 📝 Notas Importantes

- El servicio se conecta directamente a las bases de datos PostgreSQL y MongoDB
- No modifica datos, solo realiza consultas de lectura
- Todos los reportes incluyen la fecha de generación
- Los endpoints incluyen validación de parámetros
- Manejo de errores con códigos HTTP apropiados
- CORS habilitado para permitir acceso desde cualquier origen

## 🤝 Contribución

Este microservicio es parte del sistema WMS Provesi desarrollado para la Universidad de los Andes.

## 📄 Licencia

Proyecto académico - Universidad de los Andes

