from django.shortcuts import render
from .logic.producto_logic import get_productos

# Create your views here.
def productos_list(request):
    productos = get_productos()
    context = {
        'productos_list': productos.json()
    }

    return render(request, 'productos_list.html', context)