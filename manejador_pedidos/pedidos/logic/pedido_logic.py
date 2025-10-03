from ..models import Pedido

def get_pedidos():
    queryset = Pedido.objects.all()
    
    return list(queryset.values())

def get_pedido_by_id(pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    return {
        'id': pedido.id,
        'estado': pedido.estado,
        'metodo_pago': pedido.metodo_pago,
        'fecha_creacion': pedido.fecha_creacion,
        'fecha_actualizacion': pedido.fecha_actualizacion
    }

def get_pedido_items(pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    queryset = pedido.items.all()

    return list(queryset.values())