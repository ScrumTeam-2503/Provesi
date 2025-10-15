from ..models import Pedido

def get_pedidos():
    queryset = Pedido.objects.all()

    return (queryset)

def get_pedido_by_id(pedido_id):
    queryset = Pedido.objects.get(id=pedido_id)

    return (queryset)

def create_pedido(form):
    pedido = form.save()
    pedido.save()

    return pedido