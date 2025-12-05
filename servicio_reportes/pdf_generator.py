"""
Generador de reportes en PDF
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Clase para generar reportes en PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Información
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#424242'),
            alignment=TA_LEFT
        ))
        
        # Pie de página
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def _create_header(self, title, subtitle=None):
        """Crea el encabezado del reporte"""
        elements = []
        
        # Título
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtítulo si existe
        if subtitle:
            elements.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        
        # Fecha de generación
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        elements.append(Paragraph(
            f"<b>Fecha de generación:</b> {fecha}",
            self.styles['InfoText']
        ))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self):
        """Crea el pie de página"""
        return Paragraph(
            "Provesi WMS - Sistema de Gestión de Inventario | Universidad de los Andes",
            self.styles['Footer']
        )
    
    def _format_currency(self, value):
        """Formatea valores monetarios"""
        return f"${value:,.0f} COP"
    
    def _format_percentage(self, value):
        """Formatea porcentajes"""
        return f"{value:.2f}%"
    
    def generate_inventario_pdf(self, data):
        """Genera PDF del reporte de inventario"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "Reporte de Inventario",
            "Sistema WMS Provesi"
        ))
        
        # Resumen general
        elements.append(Paragraph("Resumen General", self.styles['CustomSubtitle']))
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Productos', str(data['total_productos'])],
            ['Total de Bodegas', str(data['total_bodegas'])],
            ['Total de Estanterías', str(data['total_estanterias'])],
            ['Total de Ubicaciones', str(data['total_ubicaciones'])],
            ['Stock Total', f"{data['stock_total']:,}"],
            ['Capacidad Total', f"{data['capacidad_total']:,}"],
            ['Ocupación Global', self._format_percentage(data['porcentaje_ocupacion'])],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Detalle por bodegas
        if data['bodegas']:
            elements.append(Paragraph("Detalle por Bodegas", self.styles['CustomSubtitle']))
            
            bodega_data = [['Código', 'Ciudad', 'Productos', 'Stock', 'Capacidad', 'Ocupación']]
            
            for bodega in data['bodegas']:
                bodega_data.append([
                    bodega['codigo'],
                    bodega['ciudad'],
                    str(bodega['cantidad_productos']),
                    f"{bodega['stock_total']:,}",
                    f"{bodega['capacidad_total']:,}",
                    self._format_percentage(bodega['porcentaje_ocupacion'])
                ])
            
            bodega_table = Table(bodega_data, colWidths=[0.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            bodega_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(bodega_table)
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_pedidos_pdf(self, data):
        """Genera PDF del reporte de pedidos"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "Reporte de Pedidos",
            "Sistema WMS Provesi"
        ))
        
        # Resumen general
        elements.append(Paragraph("Resumen General", self.styles['CustomSubtitle']))
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Pedidos', str(data['total_pedidos'])],
            ['Total de Items', str(data['total_items'])],
            ['Cantidad Total de Productos', f"{data['cantidad_total_productos']:,}"],
            ['Valor Total', self._format_currency(data['valor_total'])],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Pedidos por estado
        elements.append(Paragraph("Distribución por Estado", self.styles['CustomSubtitle']))
        
        estado_data = [
            ['Estado', 'Cantidad'],
            ['Pendiente', str(data['por_estado']['pendiente'])],
            ['Procesando', str(data['por_estado']['procesando'])],
            ['Enviado', str(data['por_estado']['enviado'])],
            ['Entregado', str(data['por_estado']['entregado'])],
            ['Cancelado', str(data['por_estado']['cancelado'])],
        ]
        
        estado_table = Table(estado_data, colWidths=[3*inch, 2*inch])
        estado_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(estado_table)
        elements.append(Spacer(1, 20))
        
        # Pedidos por método de pago
        elements.append(Paragraph("Distribución por Método de Pago", self.styles['CustomSubtitle']))
        
        pago_data = [
            ['Método de Pago', 'Cantidad'],
            ['Efectivo', str(data['por_metodo_pago']['efectivo'])],
            ['Transferencia', str(data['por_metodo_pago']['transferencia'])],
        ]
        
        pago_table = Table(pago_data, colWidths=[3*inch, 2*inch])
        pago_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(pago_table)
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_productos_vendidos_pdf(self, data):
        """Genera PDF del reporte de productos más vendidos"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "Reporte de Productos Más Vendidos",
            f"Top {data['limite']} Productos"
        ))
        
        # Tabla de productos
        if data['productos']:
            producto_data = [['#', 'Código', 'Nombre', 'Precio', 'Veces Pedido', 'Cant. Total', 'Valor Total']]
            
            for idx, producto in enumerate(data['productos'], 1):
                producto_data.append([
                    str(idx),
                    producto['codigo'],
                    producto['nombre'][:30] + '...' if len(producto['nombre']) > 30 else producto['nombre'],
                    self._format_currency(producto['precio']),
                    str(producto['veces_pedido']),
                    f"{producto['cantidad_total']:,}",
                    self._format_currency(producto['valor_total'])
                ])
            
            producto_table = Table(producto_data, colWidths=[0.4*inch, 0.8*inch, 2*inch, 1*inch, 0.9*inch, 0.9*inch, 1.2*inch])
            producto_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Nombre alineado a la izquierda
            ]))
            
            elements.append(producto_table)
        else:
            elements.append(Paragraph("No hay datos de productos vendidos.", self.styles['InfoText']))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_bodegas_capacidad_pdf(self, data):
        """Genera PDF del reporte de capacidad de bodegas"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "Reporte de Capacidad de Bodegas",
            "Análisis de Ocupación y Disponibilidad"
        ))
        
        # Tabla de bodegas
        if data['bodegas']:
            bodega_data = [['Código', 'Ciudad', 'Estanterías', 'Ubicaciones', 'Capacidad', 'Stock', 'Ocupación', 'Vacías', 'Llenas']]
            
            for bodega in data['bodegas']:
                bodega_data.append([
                    bodega['codigo'],
                    bodega['ciudad'],
                    str(bodega['total_estanterias']),
                    str(bodega['total_ubicaciones']),
                    f"{bodega['capacidad_total']:,}",
                    f"{bodega['stock_total']:,}",
                    self._format_percentage(bodega['porcentaje_ocupacion']),
                    str(bodega['ubicaciones_vacias']),
                    str(bodega['ubicaciones_llenas'])
                ])
            
            bodega_table = Table(bodega_data, colWidths=[0.6*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.6*inch, 0.6*inch])
            bodega_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(bodega_table)
        else:
            elements.append(Paragraph("No hay datos de bodegas.", self.styles['InfoText']))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_ventas_por_fecha_pdf(self, data):
        """Genera PDF del reporte de ventas por fecha"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Encabezado
        elements.extend(self._create_header(
            "Reporte de Ventas por Fecha",
            f"Agrupado por {data['agrupar_por']}"
        ))
        
        # Tabla de ventas
        if data['ventas']:
            venta_data = [['Fecha', 'Pedidos', 'Items', 'Cantidad Productos', 'Valor Total']]
            
            total_pedidos = 0
            total_items = 0
            total_cantidad = 0
            total_valor = 0
            
            for venta in data['ventas']:
                fecha_str = venta['fecha'] if venta['fecha'] else 'N/A'
                if venta['fecha']:
                    # Formatear fecha
                    try:
                        fecha_obj = datetime.fromisoformat(venta['fecha'])
                        if data['agrupar_por'] == 'dia':
                            fecha_str = fecha_obj.strftime('%d/%m/%Y')
                        elif data['agrupar_por'] == 'mes':
                            fecha_str = fecha_obj.strftime('%m/%Y')
                        else:  # año
                            fecha_str = fecha_obj.strftime('%Y')
                    except:
                        pass
                
                venta_data.append([
                    fecha_str,
                    str(venta['total_pedidos']),
                    str(venta['total_items']),
                    f"{venta['cantidad_productos']:,}",
                    self._format_currency(venta['valor_total'])
                ])
                
                total_pedidos += venta['total_pedidos']
                total_items += venta['total_items']
                total_cantidad += venta['cantidad_productos']
                total_valor += venta['valor_total']
            
            # Agregar fila de totales
            venta_data.append([
                'TOTAL',
                str(total_pedidos),
                str(total_items),
                f"{total_cantidad:,}",
                self._format_currency(total_valor)
            ])
            
            venta_table = Table(venta_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch, 1.5*inch])
            venta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
                # Fila de totales
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#283593')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(venta_table)
        else:
            elements.append(Paragraph("No hay datos de ventas para el período seleccionado.", self.styles['InfoText']))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        elements.append(self._create_footer())
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

