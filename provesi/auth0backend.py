import requests
import jwt
from social_core.backends.oauth import BaseOAuth2
from django.conf import settings

class Auth0(BaseOAuth2):
    """Auth0 OAuth authentication backend"""
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('picture', 'picture')
    ]

    def authorization_url(self):
        """Return the authorization endpoint."""
        return "https://" + self.setting('DOMAIN') + "/authorize"

    def access_token_url(self):
        """Return the token endpoint."""
        return "https://" + self.setting('DOMAIN') + "/oauth/token"

    def get_user_id(self, details, response):
        """Return current user id."""
        return details['user_id']

    def get_user_details(self, response):
        url = 'https://' + self.setting('DOMAIN') + '/userinfo'
        headers = {'authorization': 'Bearer ' + response['access_token']}
        resp = requests.get(url, headers=headers)
        userinfo = resp.json()
        return {
            'username': userinfo.get('nickname', ''),
            'first_name': userinfo.get('name', ''),
            'picture': userinfo.get('picture', ''),
            'user_id': userinfo.get('sub', ''),
        }

# Esta función está POR FUERA de la clase Auth0. Es una función independiente.
def getRole(request):
    user = request.user
    if not user.is_authenticated:
        return None
    # Prefer cached role in session to avoid per-request flapping
    cached_role = request.session.get('auth0_role')
    if cached_role:
        return cached_role
    auth_set = user.social_auth.filter(provider="auth0")
    if not auth_set.exists():
        return None
    auth0user = auth_set[0]

    # 1) Intentar desde el id_token (contiene claims personalizados)
    id_token = auth0user.extra_data.get('id_token')
    if id_token:
        try:
            claims = jwt.decode(id_token, options={"verify_signature": False})
            domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
            no_scheme = domain.replace('https://', '').replace('http://', '')
            possible_keys = [
                f"https://{no_scheme}/role",   # namespaced con https
                f"{no_scheme}/role",           # namespaced sin esquema (como en Action del doc)
                "role",                        # fallback simple
            ]
            for key in possible_keys:
                if key in claims:
                    role = claims[key]
                    if role:
                        request.session['auth0_role'] = role
                        return role
        except Exception:
            pass

    # 2) Fallback: userinfo endpoint (si está configurado para devolver el claim)
    try:
        access_token = auth0user.extra_data.get('access_token')
        if access_token:
            url = 'https://' + settings.SOCIAL_AUTH_AUTH0_DOMAIN + '/userinfo'
            headers = {'authorization': 'Bearer ' + access_token}
            resp = requests.get(url, headers=headers, timeout=5)
            userinfo = resp.json()
            domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
            no_scheme = domain.replace('https://', '').replace('http://', '')
            for key in (f"https://{no_scheme}/role", f"{no_scheme}/role", "role"):
                if key in userinfo:
                    role = userinfo[key]
                    if role:
                        request.session['auth0_role'] = role
                        return role
    except Exception:
        pass

    return None