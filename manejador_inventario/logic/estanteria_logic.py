def create_estanteria(form, bodega):
    """
    Crea una nueva estantería asociada a una bodega a partir de un formulario validado.
    """
    estanteria = form.save(commit=False)
    estanteria.bodega = bodega
    estanteria.save()

    return estanteria