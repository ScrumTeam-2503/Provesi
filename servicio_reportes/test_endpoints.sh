#!/bin/bash

# Script para probar los endpoints del servicio de reportes

BASE_URL="http://localhost:8000"

echo "🧪 Probando Endpoints del Servicio de Reportes"
echo "=============================================="
echo ""

# Health Check
echo "1️⃣  Health Check"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Reporte de Inventario
echo "2️⃣  Reporte de Inventario"
curl -s "$BASE_URL/reportes/inventario" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Reporte de Pedidos
echo "3️⃣  Reporte de Pedidos"
curl -s "$BASE_URL/reportes/pedidos" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Productos Más Vendidos
echo "4️⃣  Productos Más Vendidos (Top 5)"
curl -s "$BASE_URL/reportes/productos-mas-vendidos?limite=5" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Capacidad de Bodegas
echo "5️⃣  Capacidad de Bodegas"
curl -s "$BASE_URL/reportes/bodegas-capacidad" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Ventas por Fecha
echo "6️⃣  Ventas por Fecha (agrupado por mes)"
curl -s "$BASE_URL/reportes/ventas-por-fecha?agrupar_por=mes" | python3 -m json.tool
echo ""
echo "---"
echo ""

# MongoDB - Pedidos
echo "7️⃣  MongoDB - Últimos 5 Pedidos"
curl -s "$BASE_URL/reportes/mongodb/pedidos?limite=5" | python3 -m json.tool
echo ""
echo "---"
echo ""

# MongoDB - Productos
echo "8️⃣  MongoDB - Últimos 5 Productos"
curl -s "$BASE_URL/reportes/mongodb/productos?limite=5" | python3 -m json.tool
echo ""

echo "=============================================="
echo "✅ Pruebas completadas"

