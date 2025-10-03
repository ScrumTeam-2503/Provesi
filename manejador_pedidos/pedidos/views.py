from django.http import JsonResponse
from .logic.pedido_logic import get_pedidos, get_pedido_by_id, get_pedido_items

# Create your views here.
def pedidos_list(request):
    pedidos = get_pedidos()

    return JsonResponse(pedidos, safe=False)

def pedido_detail(request, id):
    pedido = get_pedido_by_id(id)
    
    pedido['factura'] = getattr(pedido, 'factura', None)
    pedido['items'] = get_pedido_items(id)

    return JsonResponse(pedido, safe=False)
