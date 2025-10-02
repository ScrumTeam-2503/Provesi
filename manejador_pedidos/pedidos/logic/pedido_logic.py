from ..models import Pedido

def get_pedidos():
    queryset = Pedido.objects.all()
    
    return list(queryset.values())

def get_pedido_by_id(pedido_id):
    return Pedido.objects.get(id=pedido_id)