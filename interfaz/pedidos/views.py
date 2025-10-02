from django.shortcuts import render
from .logic.pedido_logic import get_pedidos

# Create your views here.
def pedidos_list(request):
    pedidos = get_pedidos()
    context = {
        'pedidos_list': pedidos.json()
    }

    return render(request, 'pedidos_list.html', context)