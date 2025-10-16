from ..models import Estanteria

def get_estanteria_by_codigo(bodega_estanteria, zona_estanteria, codigo_estanteria):
    """
    Obtiene una estantería específica por su código dentro de una bodega.
    """
    estanteria = Estanteria.objects.get(bodega=bodega_estanteria, zona=zona_estanteria, codigo=codigo_estanteria)
    return estanteria

def create_estanteria(form, bodega):
    """
    Crea una nueva estantería asociada a una bodega a partir de un formulario validado.
    """
    estanteria = form.save(commit=False)
    estanteria.bodega = bodega
    estanteria.save()

    return estanteria