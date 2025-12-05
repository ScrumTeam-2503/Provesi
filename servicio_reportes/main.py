"""
Microservicio de Reportes - Provesi WMS
FastAPI service para generar reportes de inventario y pedidos
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from database import get_postgres_connection, get_mongo_db
from models import (
    ReporteInventario,
    ReportePedidos,
    ReporteProductosMasVendidos,
    ReporteBodegasCapacidad,
    ReporteVentasPorFecha,
    HealthCheck
)
from pdf_generator import PDFReportGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Provesi - Servicio de Reportes",
    description="Microservicio para generar reportes de inventario y pedidos",
    version="1.0.0"
)

# Inicializar generador de PDFs
pdf_generator = PDFReportGenerator()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheck)
async def root():
    """Endpoint de health check"""
    return {
        "status": "ok",
        "service": "Servicio de Reportes",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Verifica el estado del servicio y las conexiones a las bases de datos"""
    try:
        # Verificar PostgreSQL
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        # Verificar MongoDB
        db = get_mongo_db()
        db.command('ping')
        
        return {
            "status": "ok",
            "service": "Servicio de Reportes",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "databases": {
                "postgresql": "connected",
                "mongodb": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/reportes/inventario", response_model=ReporteInventario)
async def reporte_inventario(bodega_codigo: Optional[str] = None):
    """
    Genera un reporte completo del inventario
    
    - **bodega_codigo**: Filtrar por código de bodega (opcional)
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Query para obtener estadísticas de inventario
        query = """
            SELECT 
                COUNT(DISTINCT p.codigo) as total_productos,
                COUNT(DISTINCT b.codigo) as total_bodegas,
                COUNT(DISTINCT e.id) as total_estanterias,
                COUNT(u.id) as total_ubicaciones,
                COALESCE(SUM(u.stock), 0) as stock_total,
                COALESCE(SUM(u.capacidad), 0) as capacidad_total
            FROM manejador_inventario_producto p
            LEFT JOIN manejador_inventario_ubicacion u ON p.codigo = u.producto_id
            LEFT JOIN manejador_inventario_estanteria e ON u.estanteria_id = e.id
            LEFT JOIN manejador_inventario_bodega b ON e.bodega_id = b.codigo
        """
        
        if bodega_codigo:
            query += " WHERE b.codigo = %s"
            cursor.execute(query, (bodega_codigo,))
        else:
            cursor.execute(query)
        
        result = cursor.fetchone()
        
        # Query para productos por bodega
        productos_por_bodega_query = """
            SELECT 
                b.codigo,
                b.ciudad,
                b.direccion,
                COUNT(DISTINCT u.producto_id) as cantidad_productos,
                COALESCE(SUM(u.stock), 0) as stock_total,
                COALESCE(SUM(u.capacidad), 0) as capacidad_total
            FROM manejador_inventario_bodega b
            LEFT JOIN manejador_inventario_estanteria e ON b.codigo = e.bodega_id
            LEFT JOIN manejador_inventario_ubicacion u ON e.id = u.estanteria_id
        """
        
        if bodega_codigo:
            productos_por_bodega_query += " WHERE b.codigo = %s"
            productos_por_bodega_query += " GROUP BY b.codigo, b.ciudad, b.direccion"
            cursor.execute(productos_por_bodega_query, (bodega_codigo,))
        else:
            productos_por_bodega_query += " GROUP BY b.codigo, b.ciudad, b.direccion"
            cursor.execute(productos_por_bodega_query)
        
        bodegas = []
        for row in cursor.fetchall():
            porcentaje_ocupacion = (row[4] / row[5] * 100) if row[5] > 0 else 0
            bodegas.append({
                "codigo": row[0],
                "ciudad": row[1],
                "direccion": row[2],
                "cantidad_productos": row[3],
                "stock_total": row[4],
                "capacidad_total": row[5],
                "porcentaje_ocupacion": round(porcentaje_ocupacion, 2)
            })
        
        cursor.close()
        conn.close()
        
        porcentaje_ocupacion_global = (result[4] / result[5] * 100) if result[5] > 0 else 0
        
        return {
            "total_productos": result[0],
            "total_bodegas": result[1],
            "total_estanterias": result[2],
            "total_ubicaciones": result[3],
            "stock_total": result[4],
            "capacidad_total": result[5],
            "porcentaje_ocupacion": round(porcentaje_ocupacion_global, 2),
            "bodegas": bodegas,
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de inventario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/pedidos", response_model=ReportePedidos)
async def reporte_pedidos(
    estado: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """
    Genera un reporte de pedidos
    
    - **estado**: Filtrar por estado (pendiente, procesando, enviado, entregado, cancelado)
    - **fecha_inicio**: Fecha de inicio (formato: YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin (formato: YYYY-MM-DD)
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Query base
        query = """
            SELECT 
                COUNT(p.id) as total_pedidos,
                COUNT(CASE WHEN p.estado = 'pendiente' THEN 1 END) as pendientes,
                COUNT(CASE WHEN p.estado = 'procesando' THEN 1 END) as procesando,
                COUNT(CASE WHEN p.estado = 'enviado' THEN 1 END) as enviados,
                COUNT(CASE WHEN p.estado = 'entregado' THEN 1 END) as entregados,
                COUNT(CASE WHEN p.estado = 'cancelado' THEN 1 END) as cancelados,
                COUNT(CASE WHEN p.metodo_pago = 'efectivo' THEN 1 END) as pago_efectivo,
                COUNT(CASE WHEN p.metodo_pago = 'transferencia' THEN 1 END) as pago_transferencia
            FROM manejador_pedidos_pedido p
            WHERE 1=1
        """
        
        params = []
        
        if estado:
            query += " AND p.estado = %s"
            params.append(estado)
        
        if fecha_inicio:
            query += " AND p.fecha_creacion >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND p.fecha_creacion <= %s"
            params.append(fecha_fin)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        # Query para items por pedido
        items_query = """
            SELECT 
                COUNT(i.id) as total_items,
                COALESCE(SUM(i.cantidad), 0) as cantidad_total,
                COALESCE(SUM(i.cantidad * pr.precio), 0) as valor_total
            FROM manejador_pedidos_item i
            JOIN manejador_pedidos_pedido p ON i.pedido_id = p.id
            JOIN manejador_inventario_producto pr ON i.producto_id = pr.codigo
            WHERE 1=1
        """
        
        items_params = []
        
        if estado:
            items_query += " AND p.estado = %s"
            items_params.append(estado)
        
        if fecha_inicio:
            items_query += " AND p.fecha_creacion >= %s"
            items_params.append(fecha_inicio)
        
        if fecha_fin:
            items_query += " AND p.fecha_creacion <= %s"
            items_params.append(fecha_fin)
        
        cursor.execute(items_query, items_params)
        items_result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "total_pedidos": result[0],
            "por_estado": {
                "pendiente": result[1],
                "procesando": result[2],
                "enviado": result[3],
                "entregado": result[4],
                "cancelado": result[5]
            },
            "por_metodo_pago": {
                "efectivo": result[6],
                "transferencia": result[7]
            },
            "total_items": items_result[0],
            "cantidad_total_productos": items_result[1],
            "valor_total": items_result[2],
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de pedidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/productos-mas-vendidos", response_model=ReporteProductosMasVendidos)
async def reporte_productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=100),
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """
    Genera un reporte de los productos más vendidos
    
    - **limite**: Número de productos a retornar (1-100)
    - **fecha_inicio**: Fecha de inicio (formato: YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin (formato: YYYY-MM-DD)
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                pr.codigo,
                pr.nombre,
                pr.descripcion,
                pr.precio,
                COUNT(DISTINCT i.pedido_id) as veces_pedido,
                COALESCE(SUM(i.cantidad), 0) as cantidad_total,
                COALESCE(SUM(i.cantidad * pr.precio), 0) as valor_total
            FROM manejador_inventario_producto pr
            JOIN manejador_pedidos_item i ON pr.codigo = i.producto_id
            JOIN manejador_pedidos_pedido p ON i.pedido_id = p.id
            WHERE p.estado != 'cancelado'
        """
        
        params = []
        
        if fecha_inicio:
            query += " AND p.fecha_creacion >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND p.fecha_creacion <= %s"
            params.append(fecha_fin)
        
        query += """
            GROUP BY pr.codigo, pr.nombre, pr.descripcion, pr.precio
            ORDER BY cantidad_total DESC
            LIMIT %s
        """
        params.append(limite)
        
        cursor.execute(query, params)
        
        productos = []
        for row in cursor.fetchall():
            productos.append({
                "codigo": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "precio": row[3],
                "veces_pedido": row[4],
                "cantidad_total": row[5],
                "valor_total": row[6]
            })
        
        cursor.close()
        conn.close()
        
        return {
            "productos": productos,
            "limite": limite,
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de productos más vendidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/bodegas-capacidad", response_model=ReporteBodegasCapacidad)
async def reporte_bodegas_capacidad():
    """
    Genera un reporte de capacidad y ocupación de bodegas
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                b.codigo,
                b.ciudad,
                b.direccion,
                COUNT(DISTINCT e.id) as total_estanterias,
                COUNT(u.id) as total_ubicaciones,
                COALESCE(SUM(u.capacidad), 0) as capacidad_total,
                COALESCE(SUM(u.stock), 0) as stock_total,
                COUNT(CASE WHEN u.stock = 0 THEN 1 END) as ubicaciones_vacias,
                COUNT(CASE WHEN u.stock >= u.capacidad THEN 1 END) as ubicaciones_llenas
            FROM manejador_inventario_bodega b
            LEFT JOIN manejador_inventario_estanteria e ON b.codigo = e.bodega_id
            LEFT JOIN manejador_inventario_ubicacion u ON e.id = u.estanteria_id
            GROUP BY b.codigo, b.ciudad, b.direccion
            ORDER BY b.codigo
        """
        
        cursor.execute(query)
        
        bodegas = []
        for row in cursor.fetchall():
            capacidad_total = row[5]
            stock_total = row[6]
            porcentaje_ocupacion = (stock_total / capacidad_total * 100) if capacidad_total > 0 else 0
            
            bodegas.append({
                "codigo": row[0],
                "ciudad": row[1],
                "direccion": row[2],
                "total_estanterias": row[3],
                "total_ubicaciones": row[4],
                "capacidad_total": capacidad_total,
                "stock_total": stock_total,
                "porcentaje_ocupacion": round(porcentaje_ocupacion, 2),
                "ubicaciones_vacias": row[7],
                "ubicaciones_llenas": row[8]
            })
        
        cursor.close()
        conn.close()
        
        return {
            "bodegas": bodegas,
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de capacidad de bodegas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/ventas-por-fecha", response_model=ReporteVentasPorFecha)
async def reporte_ventas_por_fecha(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    agrupar_por: str = Query("dia", regex="^(dia|mes|año)$")
):
    """
    Genera un reporte de ventas agrupadas por fecha
    
    - **fecha_inicio**: Fecha de inicio (formato: YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin (formato: YYYY-MM-DD)
    - **agrupar_por**: Agrupar por 'dia', 'mes' o 'año'
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Determinar el formato de agrupación
        if agrupar_por == "dia":
            date_format = "DATE(p.fecha_creacion)"
        elif agrupar_por == "mes":
            date_format = "DATE_TRUNC('month', p.fecha_creacion)"
        else:  # año
            date_format = "DATE_TRUNC('year', p.fecha_creacion)"
        
        query = f"""
            SELECT 
                {date_format} as fecha,
                COUNT(DISTINCT p.id) as total_pedidos,
                COUNT(i.id) as total_items,
                COALESCE(SUM(i.cantidad), 0) as cantidad_productos,
                COALESCE(SUM(i.cantidad * pr.precio), 0) as valor_total
            FROM manejador_pedidos_pedido p
            LEFT JOIN manejador_pedidos_item i ON p.id = i.pedido_id
            LEFT JOIN manejador_inventario_producto pr ON i.producto_id = pr.codigo
            WHERE p.estado != 'cancelado'
        """
        
        params = []
        
        if fecha_inicio:
            query += " AND p.fecha_creacion >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND p.fecha_creacion <= %s"
            params.append(fecha_fin)
        
        query += f"""
            GROUP BY {date_format}
            ORDER BY fecha DESC
        """
        
        cursor.execute(query, params)
        
        ventas = []
        for row in cursor.fetchall():
            ventas.append({
                "fecha": row[0].isoformat() if row[0] else None,
                "total_pedidos": row[1],
                "total_items": row[2],
                "cantidad_productos": row[3],
                "valor_total": row[4]
            })
        
        cursor.close()
        conn.close()
        
        return {
            "ventas": ventas,
            "agrupar_por": agrupar_por,
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de ventas por fecha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/mongodb/pedidos")
async def reporte_mongodb_pedidos(limite: int = Query(10, ge=1, le=100)):
    """
    Obtiene los últimos pedidos desde MongoDB
    
    - **limite**: Número de pedidos a retornar (1-100)
    """
    try:
        db = get_mongo_db()
        pedidos_collection = db['pedidos']
        
        pedidos = list(pedidos_collection.find().sort('fecha_creacion', -1).limit(limite))
        
        # Convertir ObjectId a string
        for pedido in pedidos:
            pedido['_id'] = str(pedido['_id'])
        
        return {
            "pedidos": pedidos,
            "total": len(pedidos),
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo pedidos de MongoDB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/mongodb/productos")
async def reporte_mongodb_productos(limite: int = Query(10, ge=1, le=100)):
    """
    Obtiene productos desde MongoDB
    
    - **limite**: Número de productos a retornar (1-100)
    """
    try:
        db = get_mongo_db()
        productos_collection = db['productos']
        
        productos = list(productos_collection.find().limit(limite))
        
        # Convertir ObjectId a string
        for producto in productos:
            producto['_id'] = str(producto['_id'])
        
        return {
            "productos": productos,
            "total": len(productos),
            "fecha_generacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo productos de MongoDB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/inventario/pdf")
async def reporte_inventario_pdf(bodega_codigo: Optional[str] = None):
    """
    Genera un reporte de inventario en formato PDF
    
    - **bodega_codigo**: Filtrar por código de bodega (opcional)
    """
    try:
        # Obtener datos del reporte
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COUNT(DISTINCT p.codigo) as total_productos,
                COUNT(DISTINCT b.codigo) as total_bodegas,
                COUNT(DISTINCT e.id) as total_estanterias,
                COUNT(u.id) as total_ubicaciones,
                COALESCE(SUM(u.stock), 0) as stock_total,
                COALESCE(SUM(u.capacidad), 0) as capacidad_total
            FROM manejador_inventario_producto p
            LEFT JOIN manejador_inventario_ubicacion u ON p.codigo = u.producto_id
            LEFT JOIN manejador_inventario_estanteria e ON u.estanteria_id = e.id
            LEFT JOIN manejador_inventario_bodega b ON e.bodega_id = b.codigo
        """
        
        if bodega_codigo:
            query += " WHERE b.codigo = %s"
            cursor.execute(query, (bodega_codigo,))
        else:
            cursor.execute(query)
        
        result = cursor.fetchone()
        
        productos_por_bodega_query = """
            SELECT 
                b.codigo,
                b.ciudad,
                b.direccion,
                COUNT(DISTINCT u.producto_id) as cantidad_productos,
                COALESCE(SUM(u.stock), 0) as stock_total,
                COALESCE(SUM(u.capacidad), 0) as capacidad_total
            FROM manejador_inventario_bodega b
            LEFT JOIN manejador_inventario_estanteria e ON b.codigo = e.bodega_id
            LEFT JOIN manejador_inventario_ubicacion u ON e.id = u.estanteria_id
        """
        
        if bodega_codigo:
            productos_por_bodega_query += " WHERE b.codigo = %s"
            productos_por_bodega_query += " GROUP BY b.codigo, b.ciudad, b.direccion"
            cursor.execute(productos_por_bodega_query, (bodega_codigo,))
        else:
            productos_por_bodega_query += " GROUP BY b.codigo, b.ciudad, b.direccion"
            cursor.execute(productos_por_bodega_query)
        
        bodegas = []
        for row in cursor.fetchall():
            porcentaje_ocupacion = (row[4] / row[5] * 100) if row[5] > 0 else 0
            bodegas.append({
                "codigo": row[0],
                "ciudad": row[1],
                "direccion": row[2],
                "cantidad_productos": row[3],
                "stock_total": row[4],
                "capacidad_total": row[5],
                "porcentaje_ocupacion": round(porcentaje_ocupacion, 2)
            })
        
        cursor.close()
        conn.close()
        
        porcentaje_ocupacion_global = (result[4] / result[5] * 100) if result[5] > 0 else 0
        
        data = {
            "total_productos": result[0],
            "total_bodegas": result[1],
            "total_estanterias": result[2],
            "total_ubicaciones": result[3],
            "stock_total": result[4],
            "capacidad_total": result[5],
            "porcentaje_ocupacion": round(porcentaje_ocupacion_global, 2),
            "bodegas": bodegas,
            "fecha_generacion": datetime.now().isoformat()
        }
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_inventario_pdf(data)
        
        # Retornar PDF
        filename = f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generando PDF de inventario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/pedidos/pdf")
async def reporte_pedidos_pdf(
    estado: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """
    Genera un reporte de pedidos en formato PDF
    
    - **estado**: Filtrar por estado (pendiente, procesando, enviado, entregado, cancelado)
    - **fecha_inicio**: Fecha de inicio (formato: YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin (formato: YYYY-MM-DD)
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COUNT(p.id) as total_pedidos,
                COUNT(CASE WHEN p.estado = 'pendiente' THEN 1 END) as pendientes,
                COUNT(CASE WHEN p.estado = 'procesando' THEN 1 END) as procesando,
                COUNT(CASE WHEN p.estado = 'enviado' THEN 1 END) as enviados,
                COUNT(CASE WHEN p.estado = 'entregado' THEN 1 END) as entregados,
                COUNT(CASE WHEN p.estado = 'cancelado' THEN 1 END) as cancelados,
                COUNT(CASE WHEN p.metodo_pago = 'efectivo' THEN 1 END) as pago_efectivo,
                COUNT(CASE WHEN p.metodo_pago = 'transferencia' THEN 1 END) as pago_transferencia
            FROM manejador_pedidos_pedido p
            WHERE 1=1
        """
        
        params = []
        
        if estado:
            query += " AND p.estado = %s"
            params.append(estado)
        
        if fecha_inicio:
            query += " AND p.fecha_creacion >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND p.fecha_creacion <= %s"
            params.append(fecha_fin)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        items_query = """
            SELECT 
                COUNT(i.id) as total_items,
                COALESCE(SUM(i.cantidad), 0) as cantidad_total,
                COALESCE(SUM(i.cantidad * pr.precio), 0) as valor_total
            FROM manejador_pedidos_item i
            JOIN manejador_pedidos_pedido p ON i.pedido_id = p.id
            JOIN manejador_inventario_producto pr ON i.producto_id = pr.codigo
            WHERE 1=1
        """
        
        items_params = []
        
        if estado:
            items_query += " AND p.estado = %s"
            items_params.append(estado)
        
        if fecha_inicio:
            items_query += " AND p.fecha_creacion >= %s"
            items_params.append(fecha_inicio)
        
        if fecha_fin:
            items_query += " AND p.fecha_creacion <= %s"
            items_params.append(fecha_fin)
        
        cursor.execute(items_query, items_params)
        items_result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        data = {
            "total_pedidos": result[0],
            "por_estado": {
                "pendiente": result[1],
                "procesando": result[2],
                "enviado": result[3],
                "entregado": result[4],
                "cancelado": result[5]
            },
            "por_metodo_pago": {
                "efectivo": result[6],
                "transferencia": result[7]
            },
            "total_items": items_result[0],
            "cantidad_total_productos": items_result[1],
            "valor_total": items_result[2],
            "fecha_generacion": datetime.now().isoformat()
        }
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_pedidos_pdf(data)
        
        # Retornar PDF
        filename = f"reporte_pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generando PDF de pedidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/productos-mas-vendidos/pdf")
async def reporte_productos_mas_vendidos_pdf(
    limite: int = Query(10, ge=1, le=100),
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    """
    Genera un reporte de productos más vendidos en formato PDF
    
    - **limite**: Número de productos a retornar (1-100)
    - **fecha_inicio**: Fecha de inicio (formato: YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin (formato: YYYY-MM-DD)
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                pr.codigo,
                pr.nombre,
                pr.descripcion,
                pr.precio,
                COUNT(DISTINCT i.pedido_id) as veces_pedido,
                COALESCE(SUM(i.cantidad), 0) as cantidad_total,
                COALESCE(SUM(i.cantidad * pr.precio), 0) as valor_total
            FROM manejador_inventario_producto pr
            JOIN manejador_pedidos_item i ON pr.codigo = i.producto_id
            JOIN manejador_pedidos_pedido p ON i.pedido_id = p.id
            WHERE p.estado != 'cancelado'
        """
        
        params = []
        
        if fecha_inicio:
            query += " AND p.fecha_creacion >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND p.fecha_creacion <= %s"
            params.append(fecha_fin)
        
        query += """
            GROUP BY pr.codigo, pr.nombre, pr.descripcion, pr.precio
            ORDER BY cantidad_total DESC
            LIMIT %s
        """
        params.append(limite)
        
        cursor.execute(query, params)
        
        productos = []
        for row in cursor.fetchall():
            productos.append({
                "codigo": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "precio": row[3],
                "veces_pedido": row[4],
                "cantidad_total": row[5],
                "valor_total": row[6]
            })
        
        cursor.close()
        conn.close()
        
        data = {
            "productos": productos,
            "limite": limite,
            "fecha_generacion": datetime.now().isoformat()
        }
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_productos_vendidos_pdf(data)
        
        # Retornar PDF
        filename = f"reporte_productos_vendidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generando PDF de productos más vendidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/bodegas-capacidad/pdf")
async def reporte_bodegas_capacidad_pdf():
    """
    Genera un reporte de capacidad de bodegas en formato PDF
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                b.codigo,
                b.ciudad,
                b.direccion,
                COUNT(DISTINCT e.id) as total_estanterias,
                COUNT(u.id) as total_ubicaciones,
                COALESCE(SUM(u.capacidad), 0) as capacidad_total,
                COALESCE(SUM(u.stock), 0) as stock_total,
                COUNT(CASE WHEN u.stock = 0 THEN 1 END) as ubicaciones_vacias,
                COUNT(CASE WHEN u.stock >= u.capacidad THEN 1 END) as ubicaciones_llenas
            FROM manejador_inventario_bodega b
            LEFT JOIN manejador_inventario_estanteria e ON b.codigo = e.bodega_id
            LEFT JOIN manejador_inventario_ubicacion u ON e.id = u.estanteria_id
            GROUP BY b.codigo, b.ciudad, b.direccion
            ORDER BY b.codigo
        """
        
        cursor.execute(query)
        
        bodegas = []
        for row in cursor.fetchall():
            capacidad_total = row[5]
            stock_total = row[6]
            porcentaje_ocupacion = (stock_total / capacidad_total * 100) if capacidad_total > 0 else 0
            
            bodegas.append({
                "codigo": row[0],
                "ciudad": row[1],
                "direccion": row[2],
                "total_estanterias": row[3],
                "total_ubicaciones": row[4],
                "capacidad_total": capacidad_total,
                "stock_total": stock_total,
                "porcentaje_ocupacion": round(porcentaje_ocupacion, 2),
                "ubicaciones_vacias": row[7],
                "ubicaciones_llenas": row[8]
            })
        
        cursor.close()
        conn.close()
        
        data = {
            "bodegas": bodegas,
            "fecha_generacion": datetime.now().isoformat()
        }
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_bodegas_capacidad_pdf(data)
        
        # Retornar PDF
        filename = f"reporte_bodegas_capacidad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generando PDF de capacidad de bodegas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reportes/ventas-por-fecha/pdf")
async def reporte_ventas_por_fecha_pdf(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    agrupar_por: str = Query("dia", regex="^(dia|mes|año)$")
):
    """
    Genera un reporte de ventas por fecha en formato PDF
    
    - **fecha_inicio**: Fecha de inicio (formato: YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin (formato: YYYY-MM-DD)
    - **agrupar_por**: Agrupar por 'dia', 'mes' o 'año'
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        if agrupar_por == "dia":
            date_format = "DATE(p.fecha_creacion)"
        elif agrupar_por == "mes":
            date_format = "DATE_TRUNC('month', p.fecha_creacion)"
        else:  # año
            date_format = "DATE_TRUNC('year', p.fecha_creacion)"
        
        query = f"""
            SELECT 
                {date_format} as fecha,
                COUNT(DISTINCT p.id) as total_pedidos,
                COUNT(i.id) as total_items,
                COALESCE(SUM(i.cantidad), 0) as cantidad_productos,
                COALESCE(SUM(i.cantidad * pr.precio), 0) as valor_total
            FROM manejador_pedidos_pedido p
            LEFT JOIN manejador_pedidos_item i ON p.id = i.pedido_id
            LEFT JOIN manejador_inventario_producto pr ON i.producto_id = pr.codigo
            WHERE p.estado != 'cancelado'
        """
        
        params = []
        
        if fecha_inicio:
            query += " AND p.fecha_creacion >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND p.fecha_creacion <= %s"
            params.append(fecha_fin)
        
        query += f"""
            GROUP BY {date_format}
            ORDER BY fecha DESC
        """
        
        cursor.execute(query, params)
        
        ventas = []
        for row in cursor.fetchall():
            ventas.append({
                "fecha": row[0].isoformat() if row[0] else None,
                "total_pedidos": row[1],
                "total_items": row[2],
                "cantidad_productos": row[3],
                "valor_total": row[4]
            })
        
        cursor.close()
        conn.close()
        
        data = {
            "ventas": ventas,
            "agrupar_por": agrupar_por,
            "fecha_generacion": datetime.now().isoformat()
        }
        
        # Generar PDF
        pdf_buffer = pdf_generator.generate_ventas_por_fecha_pdf(data)
        
        # Retornar PDF
        filename = f"reporte_ventas_{agrupar_por}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generando PDF de ventas por fecha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

