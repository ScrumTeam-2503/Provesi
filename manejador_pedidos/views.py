from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import PedidoForm, ItemForm

from .logic.pedido_logic import get_pedidos, get_pedido_by_id, create_pedido
from .logic.item_logic import create_item

def pedidos_list(request):
    """
    Vista para listar todos los pedidos.
    
    Renderiza la plantilla 'pedidos_list.html' con el contexto de pedidos.
    """
    pedidos = get_pedidos()
    context = {
        'pedidos_list': pedidos
    }

    return render(request, 'pedidos_list.html', context)

def pedido_detail(request, pedido_id):
    """
    Vista para mostrar los detalles de un pedido específico.
    
    Renderiza la plantilla 'pedidos_detail.html' con el contexto del pedido.
    """
    pedido = get_pedido_by_id(pedido_id)

    context = {
        'pedido': pedido,
        'items': pedido.items.all()
    }

    return render(request, 'pedido_detail.html', context)

def pedido_create(request):
    """
    Vista para crear un nuevo pedido.
    
    Renderiza la plantilla 'pedido_create.html' con el formulario de creación de pedido.
    """
    if request.method == 'POST':
        form = PedidoForm(request.POST)

        if form.is_valid():
            pedido = create_pedido(form)
            messages.add_message(request, messages.SUCCESS, f"Pedido {pedido.id} creado exitosamente.")
            return HttpResponseRedirect(reverse('pedidosList'))
    else:
        form = PedidoForm()
    
    context = {
        'form': form
    }

    return render(request, 'pedido_create.html', context)

def item_create(request, pedido_id):
    """
    Vista para agregar un ítem a un pedido específico.
    
    Renderiza la plantilla 'item_create.html' con el formulario de creación de ítem.
    """
    pedido = get_pedido_by_id(pedido_id)

    if request.method == 'POST':
        form = ItemForm(request.POST)

        if form.is_valid():
            item = create_item(form, pedido)
            messages.add_message(request, messages.SUCCESS, f"Ítem {item.producto} agregado exitosamente.")
            return HttpResponseRedirect(reverse('pedidoDetail', args=[pedido.id]))
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'pedido': pedido
    }

    return render(request, 'item_create.html', context)