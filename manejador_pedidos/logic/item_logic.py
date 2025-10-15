def create_item(form, pedido):
    """
    Crea un nuevo ítem asociado a un pedido a partir de un formulario validado.
    """
    item = form.save(commit=False)
    item.pedido = pedido
    item.save()

    return item