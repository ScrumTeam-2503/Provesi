#!/bin/bash

# Script para probar los endpoints PDF del servicio de reportes

BASE_URL="http://localhost:8000"
OUTPUT_DIR="reportes_pdf"

echo "📄 Probando Endpoints PDF del Servicio de Reportes"
echo "=================================================="
echo ""

# Crear directorio para los PDFs
mkdir -p "$OUTPUT_DIR"
echo "📁 Directorio de salida: $OUTPUT_DIR"
echo ""

# 1. Reporte de Inventario PDF
echo "1️⃣  Descargando Reporte de Inventario (PDF)..."
curl -s "$BASE_URL/reportes/inventario/pdf" \
  --output "$OUTPUT_DIR/reporte_inventario.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_inventario.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

# 2. Reporte de Pedidos PDF
echo "2️⃣  Descargando Reporte de Pedidos (PDF)..."
curl -s "$BASE_URL/reportes/pedidos/pdf" \
  --output "$OUTPUT_DIR/reporte_pedidos.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_pedidos.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

# 3. Productos Más Vendidos PDF
echo "3️⃣  Descargando Top 10 Productos Más Vendidos (PDF)..."
curl -s "$BASE_URL/reportes/productos-mas-vendidos/pdf?limite=10" \
  --output "$OUTPUT_DIR/reporte_productos_vendidos.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_productos_vendidos.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

# 4. Capacidad de Bodegas PDF
echo "4️⃣  Descargando Reporte de Capacidad de Bodegas (PDF)..."
curl -s "$BASE_URL/reportes/bodegas-capacidad/pdf" \
  --output "$OUTPUT_DIR/reporte_bodegas_capacidad.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_bodegas_capacidad.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

# 5. Ventas por Día PDF
echo "5️⃣  Descargando Reporte de Ventas por Día (PDF)..."
curl -s "$BASE_URL/reportes/ventas-por-fecha/pdf?agrupar_por=dia" \
  --output "$OUTPUT_DIR/reporte_ventas_dia.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_ventas_dia.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

# 6. Ventas por Mes PDF
echo "6️⃣  Descargando Reporte de Ventas por Mes (PDF)..."
curl -s "$BASE_URL/reportes/ventas-por-fecha/pdf?agrupar_por=mes" \
  --output "$OUTPUT_DIR/reporte_ventas_mes.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_ventas_mes.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

# 7. Ventas por Año PDF
echo "7️⃣  Descargando Reporte de Ventas por Año (PDF)..."
curl -s "$BASE_URL/reportes/ventas-por-fecha/pdf?agrupar_por=año" \
  --output "$OUTPUT_DIR/reporte_ventas_año.pdf"
if [ $? -eq 0 ]; then
  echo "   ✅ Guardado en: $OUTPUT_DIR/reporte_ventas_año.pdf"
else
  echo "   ❌ Error al descargar"
fi
echo ""

echo "=============================================="
echo "✅ Pruebas completadas"
echo "📂 Revisa los PDFs en el directorio: $OUTPUT_DIR"
echo ""

# Listar archivos generados
echo "📋 Archivos generados:"
ls -lh "$OUTPUT_DIR"/*.pdf 2>/dev/null || echo "   No se generaron archivos PDF"

