from django.shortcuts import render
from .logic.pedido_logic import get_pedidos, get_pedido_by_id
from productos.logic.producto_logic import get_producto_by_codigo

# Create your views here.
def pedidos_list(request):
    pedidos = get_pedidos()
    context = {
        'pedidos_list': pedidos
    }

    return render(request, 'pedidos_list.html', context)

def pedido_detail(request, id):
    pedido = get_pedido_by_id(id)

    items = pedido.get('items', [])

    for item in items:
        item['producto'] = get_producto_by_codigo(item['producto'])

    context = {
        'pedido': pedido,
        'items': items
    }

    return render(request, 'pedido_detail.html', context)