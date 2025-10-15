from django.shortcuts import render

def index(request):
    """
    Vista principal de la aplicación.
    
    Renderiza la plantilla 'index.html'.
    """
    return render(request, 'index.html')
