"""
Context processors para inyectar información de autenticación en templates.
"""
from .auth0backend import get_user_role, is_admin


def auth_info(request):
    """
    Inyecta información de rol y permisos en todos los templates.
    
    Variables disponibles en templates:
    - role: Rol del usuario (default: 'operario')
    - is_admin: Boolean indicando si tiene permisos de admin
    """
    if not request.user.is_authenticated:
        return {
            'role': 'operario',
            'is_admin': False
        }
    
    role = get_user_role(request) or 'operario'
    
    return {
        'role': role,
        'is_admin': is_admin(request)
    }
