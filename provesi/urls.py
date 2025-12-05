"""provesi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from . import reportes_views

urlpatterns = [
    # Urls for admin site
    path('admin/', admin.site.urls),

    # Urls for home page
    path('', views.index, name='home'),
    path('logout/', views.logout, name='auth0_logout'),

    # Health check endpoint
    path('health/', views.health_check, name='health'),

    # Urls for manejador_pedidos app
    path('manejador_pedidos/', include('manejador_pedidos.urls')),

    # Urls for manejador_inventario app
    path('manejador_inventario/', include('manejador_inventario.urls')),

    # Urls for reportes
    path('reportes/', reportes_views.reportes_dashboard, name='reportes_dashboard'),
    path('reportes/verificar-servicio/', reportes_views.verificar_servicio_reportes, name='verificar_servicio_reportes'),
    path('reportes/descargar/inventario/', reportes_views.descargar_reporte_inventario, name='descargar_reporte_inventario'),
    path('reportes/descargar/pedidos/', reportes_views.descargar_reporte_pedidos, name='descargar_reporte_pedidos'),
    path('reportes/descargar/productos-vendidos/', reportes_views.descargar_reporte_productos_vendidos, name='descargar_reporte_productos_vendidos'),
    path('reportes/descargar/bodegas-capacidad/', reportes_views.descargar_reporte_bodegas_capacidad, name='descargar_reporte_bodegas_capacidad'),
    path('reportes/descargar/ventas-fecha/', reportes_views.descargar_reporte_ventas_fecha, name='descargar_reporte_ventas_fecha'),

    path(r'', include('django.contrib.auth.urls')),
    path(r'', include('social_django.urls')),

    
]
