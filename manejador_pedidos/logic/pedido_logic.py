from ..models import Pedido

def get_pedidos():
    """
    Obtiene todos los pedidos existentes en la base de datos.
    """
    queryset = Pedido.objects.all()
    return queryset

def get_pedido_by_id(pedido_id):
    """
    Obtiene un pedido específico por su ID.
    """
    queryset = Pedido.objects.get(id=pedido_id)
    return queryset

def create_pedido(form):
    """
    Crea un nuevo pedido a partir de un formulario validado.
    """
    pedido = form.save()
    pedido.save()
    return pedido
