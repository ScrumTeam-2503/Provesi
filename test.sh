#!/bin/bash

# ============================================================================
# Script de validación del ASR-SEC-001: Integridad de Roles
#
# Prueba que los roles no puedan ser forzados sin autenticación previa.
# Ejecutar: bash test.sh [URL_BASE]
#
# Ejemplos:
#   bash test.sh                              # Usa IP pública por defecto
#   bash test.sh http://localhost:8080        # Testing local
#   bash test.sh https://provesi.com          # Producción
# ============================================================================

# Configuración - IP pública por defecto
DEFAULT_BASE_URL="http://\"$1\":8000"
BASE_URL="${1:-$DEFAULT_BASE_URL}"
PASS_COUNT=0
FAIL_COUNT=0

# Colores para output (si el terminal los soporta)
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir headers
print_header() {
  echo ""
  echo "================================================"
  echo "  $1"
  echo "================================================"
  echo ""
}

# Función para imprimir info
print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

# Función para ejecutar test
run_test() {
  local test_name="$1"
  local url="$2"
  local expected_codes="$3"

  echo "[TEST] $test_name"
  echo "URL: $url"

  # Ejecutar curl con timeout y manejo de errores
  local response
  response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 15 "$url" 2>/dev/null || echo "000")

  # Si no hubo respuesta
  if [ "$response" = "000" ]; then
    echo -e "${RED}❌ FAIL${NC} - Sin respuesta del servidor (timeout o error de conexión)"
    echo "Verifica que el servidor esté corriendo en: $BASE_URL"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo ""
    return
  fi

  echo "Respuesta HTTP: $response"

  # Verificar si el código está en los esperados
  if echo "$expected_codes" | grep -wq "$response"; then
    echo -e "${GREEN}✅ PASS${NC} - Retorna HTTP $response"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "${RED}❌ FAIL${NC} - Retorna HTTP $response (esperado: $expected_codes)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  echo ""
}

# Verificar conectividad antes de empezar
print_header "Verificación de Conectividad"
print_info "Probando conectividad con: $BASE_URL"

# Extraer host y puerto de la URL
if [[ $BASE_URL =~ ^https?://([^:/]+)(:([0-9]+))? ]]; then
  HOST="${BASH_REMATCH[1]}"
  PORT="${BASH_REMATCH[3]:-80}"
  if [[ $BASE_URL =~ ^https ]]; then
    PORT="${BASH_REMATCH[3]:-443}"
  fi

  print_info "Host: $HOST"
  print_info "Puerto: $PORT"
else
  echo -e "${RED}Error: URL inválida${NC}"
  exit 1
fi

# Verificar disponibilidad del servidor
print_info "Verificando disponibilidad del servidor..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE_URL}/health/" 2>/dev/null || echo "000")
if [ "$HEALTH_CHECK" = "200" ]; then
  echo -e "${GREEN}✓${NC} Servidor accesible (health check: 200 OK)"
elif [ "$HEALTH_CHECK" = "302" ] || [ "$HEALTH_CHECK" = "301" ]; then
  echo -e "${GREEN}✓${NC} Servidor accesible (health check: $HEALTH_CHECK)"
elif [ "$HEALTH_CHECK" = "000" ]; then
  echo -e "${RED}✗${NC} Servidor no responde"
  echo -e "${RED}Error: No se puede conectar a $BASE_URL${NC}"
  echo ""
  echo "Verifica:"
  echo "  1. El servidor está corriendo"
  echo "  2. El puerto $PORT está abierto en el firewall"
  echo "  3. La IP/URL es correcta: $BASE_URL"
  exit 2
else
  echo -e "${YELLOW}⚠${NC} Health check retornó: $HEALTH_CHECK"
  echo -e "${YELLOW}⚠${NC} Continuando con tests de todas formas..."
fi

# Inicio de tests
print_header "ASR-SEC-001: Prueba de Integridad de Roles"

print_info "Objetivo: Verificar que NO se puedan forzar roles sin autenticación"
print_info "URL Base: $BASE_URL"
echo ""

# Test 1: Intentar forzar rol sin autenticación
run_test \
  "Forzar rol 'administrador' sin autenticación" \
  "${BASE_URL}/?test_role=administrador" \
  "302 401 403"

# Test 2: Acceder a endpoint protegido sin auth
run_test \
  "Crear bodega sin autenticación" \
  "${BASE_URL}/manejador_inventario/bodegas/create/" \
  "302 401 403"

# Test 3: Combinación de parámetro malicioso + endpoint protegido
run_test \
  "Crear bodega con parámetro test_role sin autenticación" \
  "${BASE_URL}/manejador_inventario/bodegas/create/?test_role=administrador" \
  "302 401 403"

# Test 4: Acceso a página principal
run_test \
  "Acceder a página principal" \
  "${BASE_URL}/" \
  "302 200"

# Test 5: Health check (debe ser público)
run_test \
  "Health check (endpoint público)" \
  "${BASE_URL}/health/" \
  "200"

# Test 6: Intentar acceder a productos sin auth
run_test \
  "Listar productos sin autenticación" \
  "${BASE_URL}/manejador_inventario/productos/" \
  "302 401 403"

# Test 7: Intentar crear pedido sin auth
run_test \
  "Crear pedido sin autenticación" \
  "${BASE_URL}/manejador_pedidos/pedidos/create/" \
  "302 401 403"

# Resumen final
print_header "Resumen de Pruebas"

TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo "URL Testeada: $BASE_URL"
echo "Total de tests: $TOTAL"
echo -e "${GREEN}Pasados: $PASS_COUNT${NC}"
echo -e "${RED}Fallidos: $FAIL_COUNT${NC}"

if [ $TOTAL -eq 0 ]; then
  echo ""
  echo -e "${RED}❌ ERROR${NC}"
  echo "No se pudieron ejecutar tests. Verifica:"
  echo "  1. El servidor está corriendo en: $BASE_URL"
  echo "  2. El firewall permite conexiones al puerto $PORT"
  echo "  3. La URL es correcta"
  exit 2
fi

# Calcular porcentaje
PERCENTAGE=$((PASS_COUNT * 100 / TOTAL))
echo "Porcentaje de éxito: ${PERCENTAGE}%"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
  echo -e "${GREEN}✅ ASR-SEC-001 VALIDADO EXITOSAMENTE${NC}"
  echo "El sistema cumple con los requisitos de integridad de roles."
  echo ""
  echo "Interpretación de resultados:"
  echo "  • HTTP 302: Redirección a login (correcto)"
  echo "  • HTTP 401: No autorizado (correcto)"
  echo "  • HTTP 403: Prohibido (correcto)"
  echo "  • HTTP 200: Acceso permitido (solo para endpoints públicos)"
  exit 0
else
  echo -e "${RED}❌ ASR-SEC-001 FALLÓ${NC}"
  echo "Se encontraron problemas de seguridad que deben ser corregidos."
  echo ""
  echo "Posibles causas:"
  echo "  • Endpoints no protegidos correctamente"
  echo "  • @login_required faltante en vistas"
  echo "  • Configuración incorrecta de middleware"
  exit 1
fi
