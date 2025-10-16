from ..models import Producto

def get_productos():
    """
    Obtiene todos los productos existentes en la base de datos.
    """
    queryset = Producto.objects.all()
    return (queryset)

def get_producto_by_codigo(codigo_producto):
    """
    Obtiene un producto específico por su código único.
    """
    producto = Producto.objects.get(codigo=codigo_producto)
    return producto

def create_producto(form):
    """
    Crea un nuevo producto a partir de un formulario validado.
    """
    producto = form.save()
    producto.save()

    return producto