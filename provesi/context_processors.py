from typing import Dict
from django.http import HttpRequest
from .auth0backend import getRole

def auth_info(request: HttpRequest) -> Dict[str, str]:
    """
    Inject authenticated user's role into template context.
    Defaults to 'operario' when not authenticated or on error.
    Also exposes is_admin boolean normalized for multiple role names.
    """
    role = 'operario'
    is_admin = False
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            resolved_role = getRole(request)
            if resolved_role:
                role = resolved_role
                normalized = str(resolved_role).strip().lower()
                if normalized in {'administrador', 'admin', 'gerencia campus', 'gerenciacampus'}:
                    is_admin = True
        except Exception:
            role = 'operario'
            is_admin = False
    return {
        'role': role,
        'is_admin': is_admin,
    }

