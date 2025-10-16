from ..models import Producto

def get_productos():
    """
    Obtiene todos los productos existentes en la base de datos.
    """
    queryset = Producto.objects.all()
    return (queryset)