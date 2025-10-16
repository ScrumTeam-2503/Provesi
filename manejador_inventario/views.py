from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import BodegaForm, EstanteriaForm

from .logic.bodega_logic import get_bodegas, get_bodega_by_codigo, create_bodega
from .logic.estanteria_logic import create_estanteria, get_estanteria_by_codigo

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

def bodega_detail(request, codigo_bodega):
    """
    Vista para ver los detalles de una bodega específica.
    
    Renderiza la plantilla 'bodega_detail.html' con el contexto de la bodega.
    """
    bodega = get_bodega_by_codigo(codigo_bodega)

    context = {
        'bodega': bodega,
        'estanterias': bodega.estanterias.all()
    }

    return render(request, 'bodega_detail.html', context)

def estanteria_detail(request, codigo_bodega, zona_estanteria, codigo_estanteria):
    """
    Vista para ver los detalles de una estantería específica.
    
    Renderiza la plantilla 'estanteria_detail.html' con el contexto de la estantería.
    """
    bodega = get_bodega_by_codigo(codigo_bodega)
    estanteria = get_estanteria_by_codigo(bodega, zona_estanteria, codigo_estanteria)

    context = {
        'estanteria': estanteria,
        'ubicaciones': estanteria.ubicaciones.all()
    }

    return render(request, 'estanteria_detail.html', context)

def bodega_create(request):
    """
    Vista para crear una nueva bodega.
    
    Renderiza la plantilla 'bodega_create.html' con el formulario de creación de bodega.
    """
    if request.method == 'POST':
        form = BodegaForm(request.POST)

        if form.is_valid():
            bodega = create_bodega(form)
            messages.add_message(request, messages.SUCCESS, f"Bodega {bodega.codigo} creada exitosamente.")
            return HttpResponseRedirect(reverse('bodegasList'))
    else:
        form = BodegaForm()

    context = {
        'form': form
    }

    return render(request, 'bodega_create.html', context)

def estanteria_create(request, codigo_bodega):
    """
    Vista para agregar una estantería a una bodega específica.
    
    Renderiza la plantilla 'estanteria_create.html' con el formulario de creación de estantería.
    """
    bodega = get_bodega_by_codigo(codigo_bodega)

    if request.method == 'POST':
        form = EstanteriaForm(request.POST)

        if form.is_valid():
            estanteria = create_estanteria(form, bodega)
            messages.add_message(request, messages.SUCCESS, f"Estantería {estanteria.id} creada exitosamente.")
            return HttpResponseRedirect(reverse('bodegaDetail', args=[bodega.codigo]))
    else:
        form = EstanteriaForm()

    context = {
        'form': form,
        'bodega': bodega
    }

    return render(request, 'estanteria_create.html', context)