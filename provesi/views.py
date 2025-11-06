from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """
    Vista principal de la aplicación.
    
    Renderiza la plantilla 'index.html'.
    """
    return render(request, 'index.html')

def health_check(request):
    """
    Endpoint de verificación de salud.

    Retorna un estado 200 OK si la aplicación está funcionando correctamente.
    """
    return JsonResponse({'message': 'OK'}, status=200)