from django.shortcuts import render

def bodegas_list(request):
    """
    Vista para listar todas las bodegas.
    
    Renderiza la plantilla 'bodegas_list.html' con el contexto de bodegas.
    """
    bodegas = []
    context = {
        'bodegas_list': bodegas
    }

    return render(request, 'bodegas_list.html', context)