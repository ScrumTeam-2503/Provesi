from ..models import Pedido

def get_pedido_items(pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    queryset = pedido.items.all()

    return list(queryset.values())

def create_item(form, pedido):
    item = form.save(commit=False)
    item.pedido = pedido
    item.save()

    return item