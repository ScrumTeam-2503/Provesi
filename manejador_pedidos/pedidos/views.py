from django.http import JsonResponse
from .logic.pedido_logic import get_pedidos, get_pedido_by_id

# Create your views here.
def pedidos_list(request):
    pedidos = get_pedidos()

    return JsonResponse(pedidos, safe=False)

def pedido_detail(request, id):
    pedido = get_pedido_by_id(id)
    factura = getattr(pedido, 'factura', None)
    
    context = {
        'pedido': pedido,
        'factura': factura 
    }

    return 0