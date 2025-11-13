from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import logout as django_logout
from django.conf import settings
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required

@login_required
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

def logout(request):
    """
    Cierra sesión local y en Auth0, redirigiendo al home.
    """
    django_logout(request)
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = request.build_absolute_uri('/')
    params = urlencode({'client_id': client_id, 'returnTo': return_to})
    return redirect(f"https://{domain}/v2/logout?{params}")