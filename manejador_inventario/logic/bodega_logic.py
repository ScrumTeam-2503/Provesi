from ..models import Bodega

def get_bodegas():
    """
    Obtiene todas las bodegas existentes en la base de datos.
    """
    queryset = Bodega.objects.all()
    return (queryset)

def create_bodega(form):
    """
    Crea una nueva bodega a partir de un formulario validado.
    """
    bodega = form.save()
    bodega.save()
    return bodega
