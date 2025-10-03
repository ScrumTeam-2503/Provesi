from ..models import Producto

def get_productos():
    queryset = Producto.objects.all()

    return list(queryset.values())