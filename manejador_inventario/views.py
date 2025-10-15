from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import BodegaForm

from .logic.bodega_logic import get_bodegas, get_bodega_by_id, create_bodega

def bodegas_list(request):
    """
    Vista para listar todas las bodegas.
    
    Renderiza la plantilla 'bodegas_list.html' con el contexto de bodegas.
    """
    bodegas = get_bodegas()
    context = {
        'bodegas_list': bodegas
    }

    return render(request, 'bodegas_list.html', context)

def bodega_detail(request, id_bodega):
    """
    Vista para ver los detalles de una bodega específica.
    
    Renderiza la plantilla 'bodega_detail.html' con el contexto de la bodega.
    """
    bodega = get_bodega_by_id(id_bodega)

    context = {
        'bodega': bodega
    }

    return render(request, 'bodega_detail.html', context)

def bodega_create(request):
    """
    Vista para crear una nueva bodega.
    
    Renderiza la plantilla 'bodega_create.html' con el formulario de creación de bodega.
    """
    if request.method == 'POST':
        form = BodegaForm(request.POST)

        if form.is_valid():
            bodega = create_bodega(form)
            messages.add_message(request, messages.SUCCESS, f"Bodega {bodega.id} creada exitosamente.")
            return HttpResponseRedirect(reverse('bodegasList'))
    else:
        form = BodegaForm()

    context = {
        'form': form
    }

    return render(request, 'bodega_create.html', context)