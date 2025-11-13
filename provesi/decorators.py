"""
Decoradores personalizados para control de acceso basado en roles.
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps

from .auth0backend import is_admin


def admin_required(view_func):
    """
    Decorador que requiere autenticación y rol de administrador.
    
    Si el usuario no es admin, redirige al home con mensaje de error.
    Combina @login_required con validación de rol admin.
    
    Uso:
        @admin_required
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_admin(request):
            messages.error(
                request, 
                'No tienes permisos para realizar esta acción. Se requiere rol de administrador.'
            )
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

