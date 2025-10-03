from django.http import JsonResponse
from .logic.producto_logic import get_productos

# Create your views here.
def productos_list(request):
    productos = get_productos()

    return JsonResponse(productos, safe=False)