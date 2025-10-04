from django.shortcuts import render
from .logic.producto_logic import get_productos, get_producto_by_codigo

# Create your views here.
def productos_list(request):
    productos = get_productos()
    context = {
        'productos_list': productos
    }

    return render(request, 'productos_list.html', context)

def producto_detail(request, codigo):
    producto = get_producto_by_codigo(codigo)
    context = {
        'producto': producto
    }

    return render(request, 'producto_detail.html', context)