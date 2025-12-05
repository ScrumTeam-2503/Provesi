"""
Modelos Pydantic para el servicio de reportes
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class HealthCheck(BaseModel):
    """Modelo para health check"""
    status: str
    service: str
    version: str
    timestamp: str
    databases: Optional[Dict[str, str]] = None


class BodegaInfo(BaseModel):
    """Información de una bodega"""
    codigo: str
    ciudad: str
    direccion: str
    cantidad_productos: int
    stock_total: int
    capacidad_total: int
    porcentaje_ocupacion: float


class ReporteInventario(BaseModel):
    """Reporte completo de inventario"""
    total_productos: int
    total_bodegas: int
    total_estanterias: int
    total_ubicaciones: int
    stock_total: int
    capacidad_total: int
    porcentaje_ocupacion: float
    bodegas: List[BodegaInfo]
    fecha_generacion: str


class EstadoPedidos(BaseModel):
    """Conteo de pedidos por estado"""
    pendiente: int
    procesando: int
    enviado: int
    entregado: int
    cancelado: int


class MetodoPago(BaseModel):
    """Conteo de pedidos por método de pago"""
    efectivo: int
    transferencia: int


class ReportePedidos(BaseModel):
    """Reporte de pedidos"""
    total_pedidos: int
    por_estado: EstadoPedidos
    por_metodo_pago: MetodoPago
    total_items: int
    cantidad_total_productos: int
    valor_total: int
    fecha_generacion: str


class ProductoVendido(BaseModel):
    """Información de un producto vendido"""
    codigo: str
    nombre: str
    descripcion: str
    precio: int
    veces_pedido: int
    cantidad_total: int
    valor_total: int


class ReporteProductosMasVendidos(BaseModel):
    """Reporte de productos más vendidos"""
    productos: List[ProductoVendido]
    limite: int
    fecha_generacion: str


class BodegaCapacidad(BaseModel):
    """Información de capacidad de una bodega"""
    codigo: str
    ciudad: str
    direccion: str
    total_estanterias: int
    total_ubicaciones: int
    capacidad_total: int
    stock_total: int
    porcentaje_ocupacion: float
    ubicaciones_vacias: int
    ubicaciones_llenas: int


class ReporteBodegasCapacidad(BaseModel):
    """Reporte de capacidad de bodegas"""
    bodegas: List[BodegaCapacidad]
    fecha_generacion: str


class VentaPorFecha(BaseModel):
    """Venta agrupada por fecha"""
    fecha: Optional[str]
    total_pedidos: int
    total_items: int
    cantidad_productos: int
    valor_total: int


class ReporteVentasPorFecha(BaseModel):
    """Reporte de ventas por fecha"""
    ventas: List[VentaPorFecha]
    agrupar_por: str
    fecha_generacion: str

