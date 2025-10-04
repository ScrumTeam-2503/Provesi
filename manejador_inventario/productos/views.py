from django.http import JsonResponse
from .logic.producto_logic import get_productos, get_producto_by_codigo

# Create your views here.
def productos_list(request):
    productos = get_productos()

    return JsonResponse(productos, safe=False)

def producto_detail(request, codigo):
    producto = get_producto_by_codigo(codigo)

    return JsonResponse(producto, safe=False)
