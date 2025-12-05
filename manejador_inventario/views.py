"""
Vistas para el módulo de gestión de inventario.
Maneja bodegas, estanterías, ubicaciones y productos.
"""
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from provesi.decorators import admin_required
from .forms import BodegaForm, EstanteriaForm, UbicacionForm, ProductoForm
from .logic.bodega_logic import get_bodegas, get_bodega_by_codigo, create_bodega
from .logic.estanteria_logic import create_estanteria, get_estanteria_by_codigo
from .logic.ubicacion_logic import create_ubicacion
from .logic.producto_logic import get_productos, get_producto_by_codigo, create_producto


# ============================================================================
# VISTAS DE LECTURA (Solo requieren login)
# ============================================================================

@login_required
def bodegas_list(request):
    """Lista todas las bodegas del sistema."""
    bodegas = get_bodegas()
    context = {
        'bodegas_list': bodegas.order_by('codigo')
    }
    return render(request, 'bodegas_list.html', context)


@login_required
def bodega_detail(request, codigo_bodega):
    """Muestra detalles de una bodega específica y sus estanterías."""
    bodega = get_bodega_by_codigo(codigo_bodega)
    context = {
        'bodega': bodega,
        'estanterias': bodega.estanterias.all().order_by('zona', 'codigo')
    }
    return render(request, 'bodega_detail.html', context)


@login_required
def estanteria_detail(request, codigo_bodega, zona_estanteria, codigo_estanteria):
    """Muestra detalles de una estantería y sus ubicaciones."""
    bodega = get_bodega_by_codigo(codigo_bodega)
    estanteria = get_estanteria_by_codigo(bodega, zona_estanteria, codigo_estanteria)
    context = {
        'estanteria': estanteria,
        'ubicaciones': estanteria.ubicaciones.all().order_by('estanteria__zona', 'estanteria__codigo', 'codigo')
    }
    return render(request, 'estanteria_detail.html', context)


@login_required
def productos_list(request):
    """Lista todos los productos del sistema."""
    productos = get_productos()
    context = {
        'productos_list': productos
    }
    return render(request, 'productos_list.html', context)


@login_required
def producto_detail(request, codigo_producto):
    """Muestra detalles de un producto y sus ubicaciones."""
    producto = get_producto_by_codigo(codigo_producto)
    context = {
        'producto': producto,
        'ubicaciones': producto.ubicaciones.all()
    }
    return render(request, 'producto_detail.html', context)


# ============================================================================
# VISTAS DE CREACIÓN (Requieren rol de administrador)
# ============================================================================

@admin_required
def bodega_create(request):
    """Crea una nueva bodega. Solo administradores."""
    if request.method == 'POST':
        form = BodegaForm(request.POST)
        if form.is_valid():
            bodega = create_bodega(form)
            
            # SINCRONIZAR A MONGODB
            from provesi.mongodb_sync import sync_bodega_to_mongo
            sync_bodega_to_mongo(bodega)
            
            messages.success(request, f"Bodega {bodega.codigo} creada exitosamente.")
            return HttpResponseRedirect(reverse('bodegasList'))
    else:
        form = BodegaForm()

    context = {
        'form': form,
        'titulo': 'Crear Bodega',
        'accion': 'Guardar Bodega',
        'cancel_url': reverse('bodegasList')
    }
    return render(request, 'create_form.html', context)


@admin_required
def estanteria_create(request, codigo_bodega):
    """Crea una nueva estantería en una bodega. Solo administradores."""
    bodega = get_bodega_by_codigo(codigo_bodega)

    if request.method == 'POST':
        form = EstanteriaForm(request.POST)
        if form.is_valid():
            estanteria = create_estanteria(form, bodega)
            messages.success(request, f"Estantería {estanteria.id} creada exitosamente.")
            return HttpResponseRedirect(reverse('bodegaDetail', args=[bodega.codigo]))
    else:
        form = EstanteriaForm()

    context = {
        'form': form,
        'bodega': bodega,
        'titulo': 'Agregar Estanteria',
        'accion': 'Guardar Estanteria',
        'cancel_url': reverse('bodegaDetail', args=[bodega.codigo])
    }
    return render(request, 'create_form.html', context)


@admin_required
def ubicacion_create(request, codigo_bodega, zona_estanteria, codigo_estanteria):
    """Crea una nueva ubicación en una estantería. Solo administradores."""
    bodega = get_bodega_by_codigo(codigo_bodega)
    estanteria = get_estanteria_by_codigo(bodega, zona_estanteria, codigo_estanteria)

    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            ubicacion = create_ubicacion(form, estanteria)
            messages.success(request, f"Ubicación {ubicacion.id} creada exitosamente.")
            return HttpResponseRedirect(reverse('estanteriaDetail', args=[bodega.codigo, estanteria.zona, estanteria.codigo]))
    else:
        form = UbicacionForm()

    context = {
        'form': form,
        'bodega': bodega,
        'estanteria': estanteria,
        'titulo': 'Agregar Ubicación',
        'accion': 'Guardar Ubicación',
        'cancel_url': reverse('estanteriaDetail', args=[bodega.codigo, estanteria.zona, estanteria.codigo])
    }
    return render(request, 'create_form.html', context)


@admin_required
def producto_create(request):
    """Crea un nuevo producto. Solo administradores."""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = create_producto(form)
            
            # SINCRONIZAR A MONGODB
            from provesi.mongodb_sync import sync_producto_to_mongo
            sync_producto_to_mongo(producto)
            
            messages.success(request, f"Producto {producto.codigo} creado exitosamente.")
            return HttpResponseRedirect(reverse('productosList'))
    else:
        form = ProductoForm()

    context = {
        'form': form,
        'titulo': 'Crear Producto',
        'accion': 'Guardar Producto',
        'cancel_url': reverse('productosList')
    }
    return render(request, 'create_form.html', context)
