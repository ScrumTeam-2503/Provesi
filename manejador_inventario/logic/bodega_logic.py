from ..models import Bodega

def get_bodegas():
    """
    Obtiene todas las bodegas existentes en la base de datos.
    """
    queryset = Bodega.objects.all()
    return (queryset)

def get_bodega_by_id(id_bodega):
    """
    Obtiene una bodega específica por su ID.
    """
    bodega = Bodega.objects.get(id=id_bodega)
    return bodega

def create_bodega(form):
    """
    Crea una nueva bodega a partir de un formulario validado.
    """
    bodega = form.save()
    bodega.save()
    return bodega
