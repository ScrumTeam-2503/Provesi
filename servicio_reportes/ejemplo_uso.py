"""
Ejemplo de uso del Servicio de Reportes - Provesi WMS

Este script muestra cómo consumir los endpoints del servicio de reportes
tanto para obtener datos JSON como para descargar reportes en PDF.
"""

import requests
import json
from datetime import datetime, timedelta

# URL base del servicio
BASE_URL = "http://localhost:8000"


def health_check():
    """Verifica que el servicio esté funcionando"""
    print("🔍 Verificando estado del servicio...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Servicio: {data['service']}")
        print(f"✅ Estado: {data['status']}")
        if 'databases' in data:
            print(f"✅ PostgreSQL: {data['databases']['postgresql']}")
            print(f"✅ MongoDB: {data['databases']['mongodb']}")
    else:
        print(f"❌ Error: {response.status_code}")
    print()


def obtener_reporte_inventario_json():
    """Obtiene el reporte de inventario en formato JSON"""
    print("📊 Obteniendo reporte de inventario (JSON)...")
    response = requests.get(f"{BASE_URL}/reportes/inventario")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total de productos: {data['total_productos']}")
        print(f"   Total de bodegas: {data['total_bodegas']}")
        print(f"   Stock total: {data['stock_total']}")
        print(f"   Ocupación: {data['porcentaje_ocupacion']}%")
        print(f"   Bodegas: {len(data['bodegas'])}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def descargar_reporte_inventario_pdf():
    """Descarga el reporte de inventario en formato PDF"""
    print("📄 Descargando reporte de inventario (PDF)...")
    response = requests.get(f"{BASE_URL}/reportes/inventario/pdf")
    
    if response.status_code == 200:
        filename = f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ PDF guardado: {filename}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def obtener_reporte_pedidos_json(estado=None):
    """Obtiene el reporte de pedidos en formato JSON"""
    print(f"📊 Obteniendo reporte de pedidos (JSON){f' - Estado: {estado}' if estado else ''}...")
    
    params = {}
    if estado:
        params['estado'] = estado
    
    response = requests.get(f"{BASE_URL}/reportes/pedidos", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total de pedidos: {data['total_pedidos']}")
        print(f"   Pendientes: {data['por_estado']['pendiente']}")
        print(f"   Procesando: {data['por_estado']['procesando']}")
        print(f"   Enviados: {data['por_estado']['enviado']}")
        print(f"   Entregados: {data['por_estado']['entregado']}")
        print(f"   Valor total: ${data['valor_total']:,} COP")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def descargar_reporte_pedidos_pdf():
    """Descarga el reporte de pedidos en formato PDF"""
    print("📄 Descargando reporte de pedidos (PDF)...")
    response = requests.get(f"{BASE_URL}/reportes/pedidos/pdf")
    
    if response.status_code == 200:
        filename = f"reporte_pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ PDF guardado: {filename}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def obtener_productos_mas_vendidos_json(limite=10):
    """Obtiene el reporte de productos más vendidos en formato JSON"""
    print(f"📊 Obteniendo top {limite} productos más vendidos (JSON)...")
    
    params = {'limite': limite}
    response = requests.get(f"{BASE_URL}/reportes/productos-mas-vendidos", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Productos encontrados: {len(data['productos'])}")
        
        if data['productos']:
            print("\n   Top 5:")
            for idx, producto in enumerate(data['productos'][:5], 1):
                print(f"   {idx}. {producto['nombre']} - Vendidos: {producto['cantidad_total']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def descargar_productos_mas_vendidos_pdf(limite=10):
    """Descarga el reporte de productos más vendidos en formato PDF"""
    print(f"📄 Descargando top {limite} productos más vendidos (PDF)...")
    
    params = {'limite': limite}
    response = requests.get(f"{BASE_URL}/reportes/productos-mas-vendidos/pdf", params=params)
    
    if response.status_code == 200:
        filename = f"reporte_productos_vendidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ PDF guardado: {filename}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def obtener_capacidad_bodegas_json():
    """Obtiene el reporte de capacidad de bodegas en formato JSON"""
    print("📊 Obteniendo reporte de capacidad de bodegas (JSON)...")
    response = requests.get(f"{BASE_URL}/reportes/bodegas-capacidad")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Bodegas encontradas: {len(data['bodegas'])}")
        
        if data['bodegas']:
            print("\n   Resumen por bodega:")
            for bodega in data['bodegas']:
                print(f"   - {bodega['codigo']} ({bodega['ciudad']}): {bodega['porcentaje_ocupacion']}% ocupación")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def descargar_capacidad_bodegas_pdf():
    """Descarga el reporte de capacidad de bodegas en formato PDF"""
    print("📄 Descargando reporte de capacidad de bodegas (PDF)...")
    response = requests.get(f"{BASE_URL}/reportes/bodegas-capacidad/pdf")
    
    if response.status_code == 200:
        filename = f"reporte_bodegas_capacidad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ PDF guardado: {filename}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def obtener_ventas_por_fecha_json(agrupar_por='mes'):
    """Obtiene el reporte de ventas por fecha en formato JSON"""
    print(f"📊 Obteniendo reporte de ventas por {agrupar_por} (JSON)...")
    
    params = {'agrupar_por': agrupar_por}
    response = requests.get(f"{BASE_URL}/reportes/ventas-por-fecha", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Registros encontrados: {len(data['ventas'])}")
        
        if data['ventas']:
            print(f"\n   Últimos 3 períodos:")
            for venta in data['ventas'][:3]:
                print(f"   - {venta['fecha']}: {venta['total_pedidos']} pedidos, ${venta['valor_total']:,} COP")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def descargar_ventas_por_fecha_pdf(agrupar_por='mes'):
    """Descarga el reporte de ventas por fecha en formato PDF"""
    print(f"📄 Descargando reporte de ventas por {agrupar_por} (PDF)...")
    
    params = {'agrupar_por': agrupar_por}
    response = requests.get(f"{BASE_URL}/reportes/ventas-por-fecha/pdf", params=params)
    
    if response.status_code == 200:
        filename = f"reporte_ventas_{agrupar_por}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   ✅ PDF guardado: {filename}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    print()


def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("=" * 60)
    print("  Ejemplo de Uso - Servicio de Reportes Provesi WMS")
    print("=" * 60)
    print()
    
    try:
        # 1. Health check
        health_check()
        
        # 2. Reportes de Inventario
        obtener_reporte_inventario_json()
        descargar_reporte_inventario_pdf()
        
        # 3. Reportes de Pedidos
        obtener_reporte_pedidos_json()
        descargar_reporte_pedidos_pdf()
        
        # 4. Productos Más Vendidos
        obtener_productos_mas_vendidos_json(limite=10)
        descargar_productos_mas_vendidos_pdf(limite=10)
        
        # 5. Capacidad de Bodegas
        obtener_capacidad_bodegas_json()
        descargar_capacidad_bodegas_pdf()
        
        # 6. Ventas por Fecha
        obtener_ventas_por_fecha_json(agrupar_por='mes')
        descargar_ventas_por_fecha_pdf(agrupar_por='mes')
        
        print("=" * 60)
        print("✅ Ejemplos completados exitosamente")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servicio.")
        print("   Asegúrate de que el servicio esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()

