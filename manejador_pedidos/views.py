"""
Vistas para el módulo de gestión de pedidos.
Maneja pedidos e ítems de pedido.
"""
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from provesi.decorators import admin_required
from .forms import PedidoForm, ItemForm
from .logic.pedido_logic import get_pedidos, get_pedido_by_id, create_pedido
from .logic.item_logic import create_item


# ============================================================================
# VISTAS DE LECTURA (Solo requieren login)
# ============================================================================

@login_required
def pedidos_list(request):
    """Lista todos los pedidos del sistema."""
    pedidos = get_pedidos()
    context = {
        'pedidos_list': pedidos
    }
    return render(request, 'pedidos_list.html', context)


@login_required
def pedido_detail(request, pedido_id):
    """Muestra detalles de un pedido específico y sus ítems."""
    pedido = get_pedido_by_id(pedido_id)
    context = {
        'pedido': pedido,
        'items': pedido.items.all()
    }
    return render(request, 'pedido_detail.html', context)


# ============================================================================
# VISTAS DE CREACIÓN (Requieren rol de administrador)
# ============================================================================

@admin_required
def pedido_create(request):
    """Crea un nuevo pedido. Solo administradores."""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = create_pedido(form)
            messages.success(request, f"Pedido {pedido.id} creado exitosamente.")
            return HttpResponseRedirect(reverse('pedidosList'))
    else:
        form = PedidoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Pedido',
        'accion': 'Guardar Pedido',
        'cancel_url': reverse('pedidosList')
    }
    return render(request, 'create_form.html', context)


@admin_required
def item_create(request, pedido_id):
    """Agrega un ítem a un pedido existente. Solo administradores."""
    pedido = get_pedido_by_id(pedido_id)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = create_item(form, pedido)
            messages.success(request, f"Ítem {item.producto} agregado exitosamente.")
            return HttpResponseRedirect(reverse('pedidoDetail', args=[pedido.id]))
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'pedido': pedido,
        'titulo': 'Agregar Item',
        'accion': 'Guardar Item',
        'cancel_url': reverse('pedidoDetail', args=[pedido.id])
    }
    return render(request, 'create_form.html', context)
