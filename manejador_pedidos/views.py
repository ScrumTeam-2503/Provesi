from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import PedidoForm

from .logic.pedido_logic import get_pedidos, create_pedido

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