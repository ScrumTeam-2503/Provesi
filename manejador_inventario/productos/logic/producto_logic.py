from ..models import Producto

def get_productos():
    queryset = Producto.objects.all()

    return list(queryset.values())

def get_producto_by_codigo(codigo_producto):
    pedido = Producto.objects.get(codigo=codigo_producto)

    return {
        'codigo': pedido.codigo,
        'nombre': pedido.nombre,
        'descripcion': pedido.descripcion,
        'precio': pedido.precio
    }