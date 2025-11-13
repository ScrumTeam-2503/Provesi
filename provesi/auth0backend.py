"""
Auth0 Backend y utilidades de autenticación.
Maneja la integración con Auth0 y extracción de roles de usuario.
"""
import requests
import jwt
from social_core.backends.oauth import BaseOAuth2
from django.conf import settings


class Auth0(BaseOAuth2):
    """Backend de autenticación OAuth2 para Auth0"""
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('picture', 'picture'),
        ('id_token', 'id_token')  # Importante: guardar id_token para claims
    ]

    def authorization_url(self):
        """Endpoint de autorización de Auth0"""
        return f"https://{self.setting('DOMAIN')}/authorize"

    def access_token_url(self):
        """Endpoint de token de Auth0"""
        return f"https://{self.setting('DOMAIN')}/oauth/token"

    def get_user_id(self, details, response):
        """Retorna el ID único del usuario"""
        return details['user_id']

    def get_user_details(self, response):
        """Obtiene detalles del usuario desde Auth0"""
        url = f"https://{self.setting('DOMAIN')}/userinfo"
        headers = {'authorization': f"Bearer {response['access_token']}"}
        resp = requests.get(url, headers=headers)
        userinfo = resp.json()
        return {
            'username': userinfo.get('nickname', ''),
            'first_name': userinfo.get('name', ''),
            'picture': userinfo.get('picture', ''),
            'user_id': userinfo.get('sub', ''),
        }


def get_user_role(request):
    """
    Obtiene el rol del usuario autenticado desde Auth0.
    
    Busca el rol en:
    1. Cache de sesión (para evitar llamadas repetidas)
    2. Claims del id_token (método preferido)
    3. Endpoint /userinfo (fallback)
    
    Returns:
        str: Rol del usuario o None si no está autenticado/no tiene rol
    """
    if not request.user.is_authenticated:
        return None
    
    # 1. Verificar cache en sesión
    cached_role = request.session.get('auth0_role')
    if cached_role:
        return cached_role
    
    try:
        # Obtener datos de Auth0
        auth0user = request.user.social_auth.filter(provider="auth0").first()
        if not auth0user:
            return None
        
        role = None
        domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN.replace('https://', '').replace('http://', '')
        
        # Posibles keys donde puede estar el claim de rol
        possible_keys = [
            f"https://{domain}/role",  # Con https://
            f"{domain}/role",          # Sin esquema
            "role"                     # Simple
        ]
        
        # 2. Intentar desde id_token (contiene claims personalizados)
        id_token = auth0user.extra_data.get('id_token')
        if id_token:
            try:
                claims = jwt.decode(id_token, options={"verify_signature": False})
                for key in possible_keys:
                    if key in claims and claims[key]:
                        role = claims[key]
                        break
            except Exception:
                pass
        
        # 3. Fallback: userinfo endpoint
        if not role:
            access_token = auth0user.extra_data.get('access_token')
            if access_token:
                try:
                    url = f"https://{domain}/userinfo"
                    headers = {'authorization': f'Bearer {access_token}'}
                    resp = requests.get(url, headers=headers, timeout=5)
                    userinfo = resp.json()
                    
                    for key in possible_keys:
                        if key in userinfo and userinfo[key]:
                            role = userinfo[key]
                            break
                except Exception:
                    pass
        
        # Guardar en cache de sesión
        if role:
            request.session['auth0_role'] = role
        
        return role
        
    except Exception:
        return None


def is_admin(request):
    """
    Verifica si el usuario tiene permisos de administrador.
    
    Roles considerados como admin:
    - administrador
    - admin
    - gerencia campus
    
    Returns:
        bool: True si el usuario es admin, False en caso contrario
    """
    role = get_user_role(request)
    if not role:
        return False
    
    # Normalizar y comparar
    normalized = str(role).strip().lower()
    admin_roles = {'administrador', 'admin'}
    
    return normalized in admin_roles
