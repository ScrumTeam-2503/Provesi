"""
Vistas para la gestión de reportes
"""
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

# URL del microservicio de reportes
# Se configura vía variable de entorno en runtime
# Desarrollo: http://localhost:8000
# Producción: Se inyecta la IP real desde Terraform/deployment script
REPORTES_SERVICE_URL = os.getenv('REPORTES_SERVICE_URL', 'http://localhost:8000')


@login_required
def reportes_dashboard(request):
    """
    Vista del dashboard de reportes.
    Muestra la página con los botones para generar reportes.
    """
    context = {
        'reportes_service_url': REPORTES_SERVICE_URL,
    }
    return render(request, 'reportes/dashboard.html', context)


@login_required
def descargar_reporte_inventario(request):
    """
    Descarga el reporte de inventario en PDF
    """
    try:
        bodega_codigo = request.GET.get('bodega_codigo', None)
        
        # Construir URL con parámetros
        url = f"{REPORTES_SERVICE_URL}/reportes/inventario/pdf"
        params = {}
        if bodega_codigo:
            params['bodega_codigo'] = bodega_codigo
        
        # Hacer petición al microservicio
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Retornar el PDF
            http_response = HttpResponse(response.content, content_type='application/pdf')
            http_response['Content-Disposition'] = response.headers.get(
                'Content-Disposition', 
                'attachment; filename="reporte_inventario.pdf"'
            )
            return http_response
        else:
            logger.error(f"Error al obtener reporte: {response.status_code}")
            return JsonResponse({
                'error': 'Error al generar el reporte',
                'details': response.text
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio de reportes: {e}")
        return JsonResponse({
            'error': 'No se pudo conectar con el servicio de reportes',
            'details': str(e)
        }, status=503)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return JsonResponse({
            'error': 'Error inesperado al generar el reporte',
            'details': str(e)
        }, status=500)


@login_required
def descargar_reporte_pedidos(request):
    """
    Descarga el reporte de pedidos en PDF
    """
    try:
        estado = request.GET.get('estado', None)
        fecha_inicio = request.GET.get('fecha_inicio', None)
        fecha_fin = request.GET.get('fecha_fin', None)
        
        # Construir URL con parámetros
        url = f"{REPORTES_SERVICE_URL}/reportes/pedidos/pdf"
        params = {}
        if estado:
            params['estado'] = estado
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
        
        # Hacer petición al microservicio
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Retornar el PDF
            http_response = HttpResponse(response.content, content_type='application/pdf')
            http_response['Content-Disposition'] = response.headers.get(
                'Content-Disposition', 
                'attachment; filename="reporte_pedidos.pdf"'
            )
            return http_response
        else:
            logger.error(f"Error al obtener reporte: {response.status_code}")
            return JsonResponse({
                'error': 'Error al generar el reporte',
                'details': response.text
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio de reportes: {e}")
        return JsonResponse({
            'error': 'No se pudo conectar con el servicio de reportes',
            'details': str(e)
        }, status=503)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return JsonResponse({
            'error': 'Error inesperado al generar el reporte',
            'details': str(e)
        }, status=500)


@login_required
def descargar_reporte_productos_vendidos(request):
    """
    Descarga el reporte de productos más vendidos en PDF
    """
    try:
        limite = request.GET.get('limite', '10')
        fecha_inicio = request.GET.get('fecha_inicio', None)
        fecha_fin = request.GET.get('fecha_fin', None)
        
        # Construir URL con parámetros
        url = f"{REPORTES_SERVICE_URL}/reportes/productos-mas-vendidos/pdf"
        params = {'limite': limite}
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
        
        # Hacer petición al microservicio
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Retornar el PDF
            http_response = HttpResponse(response.content, content_type='application/pdf')
            http_response['Content-Disposition'] = response.headers.get(
                'Content-Disposition', 
                'attachment; filename="reporte_productos_vendidos.pdf"'
            )
            return http_response
        else:
            logger.error(f"Error al obtener reporte: {response.status_code}")
            return JsonResponse({
                'error': 'Error al generar el reporte',
                'details': response.text
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio de reportes: {e}")
        return JsonResponse({
            'error': 'No se pudo conectar con el servicio de reportes',
            'details': str(e)
        }, status=503)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return JsonResponse({
            'error': 'Error inesperado al generar el reporte',
            'details': str(e)
        }, status=500)


@login_required
def descargar_reporte_bodegas_capacidad(request):
    """
    Descarga el reporte de capacidad de bodegas en PDF
    """
    try:
        url = f"{REPORTES_SERVICE_URL}/reportes/bodegas-capacidad/pdf"
        
        # Hacer petición al microservicio
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Retornar el PDF
            http_response = HttpResponse(response.content, content_type='application/pdf')
            http_response['Content-Disposition'] = response.headers.get(
                'Content-Disposition', 
                'attachment; filename="reporte_bodegas_capacidad.pdf"'
            )
            return http_response
        else:
            logger.error(f"Error al obtener reporte: {response.status_code}")
            return JsonResponse({
                'error': 'Error al generar el reporte',
                'details': response.text
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio de reportes: {e}")
        return JsonResponse({
            'error': 'No se pudo conectar con el servicio de reportes',
            'details': str(e)
        }, status=503)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return JsonResponse({
            'error': 'Error inesperado al generar el reporte',
            'details': str(e)
        }, status=500)


@login_required
def descargar_reporte_ventas_fecha(request):
    """
    Descarga el reporte de ventas por fecha en PDF
    """
    try:
        agrupar_por = request.GET.get('agrupar_por', 'mes')
        fecha_inicio = request.GET.get('fecha_inicio', None)
        fecha_fin = request.GET.get('fecha_fin', None)
        
        # Construir URL con parámetros
        url = f"{REPORTES_SERVICE_URL}/reportes/ventas-por-fecha/pdf"
        params = {'agrupar_por': agrupar_por}
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
        
        # Hacer petición al microservicio
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Retornar el PDF
            http_response = HttpResponse(response.content, content_type='application/pdf')
            http_response['Content-Disposition'] = response.headers.get(
                'Content-Disposition', 
                'attachment; filename="reporte_ventas.pdf"'
            )
            return http_response
        else:
            logger.error(f"Error al obtener reporte: {response.status_code}")
            return JsonResponse({
                'error': 'Error al generar el reporte',
                'details': response.text
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio de reportes: {e}")
        return JsonResponse({
            'error': 'No se pudo conectar con el servicio de reportes',
            'details': str(e)
        }, status=503)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return JsonResponse({
            'error': 'Error inesperado al generar el reporte',
            'details': str(e)
        }, status=500)


@login_required
def verificar_servicio_reportes(request):
    """
    Verifica que el servicio de reportes esté disponible
    """
    try:
        url = f"{REPORTES_SERVICE_URL}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'status': 'ok',
                'service': data.get('service', 'Servicio de Reportes'),
                'version': data.get('version', '1.0.0'),
                'databases': data.get('databases', {})
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Servicio no disponible'
            }, status=503)
            
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': 'No se pudo conectar con el servicio de reportes',
            'details': str(e)
        }, status=503)

