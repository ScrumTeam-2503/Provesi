from django.shortcuts import render
from .models import Pedido

from .logic.pedido_logic import get_pedidos

def pedidos_list(request):
    """
    Vista para listar todos los pedidos.
    
    Renderiza la plantilla 'pedidos_list.html' con el contexto de pedidos.
    """
    pedidos = get_pedidos()
    context = {
        'pedidos': pedidos
    }

    return render(request, 'pedidos_list.html', context)