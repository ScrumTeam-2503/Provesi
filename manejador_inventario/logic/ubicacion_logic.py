def create_ubicacion(form, estanteria):
    """
    Crea una nueva ubicación asociada a una estantería a partir de un formulario validado.
    """
    ubicacion = form.save(commit=False)
    ubicacion.estanteria = estanteria
    ubicacion.save()

    return ubicacion