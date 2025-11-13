# 📝 Resumen de Cambios - Sistema de Autenticación Auth0

## 🎯 Objetivo
Implementar un sistema de autenticación y autorización basado en roles usando Auth0, donde:
- **Administradores**: pueden ver y crear/editar todo
- **Operarios**: solo pueden ver (solo lectura)

---

## ✨ Archivos Nuevos Creados

### 1. `provesi/auth0backend.py`
**Propósito:** Backend de autenticación y lógica centralizada de roles

**Funciones principales:**
- `class Auth0(BaseOAuth2)` - Backend OAuth2 para Django Social Auth
- `get_user_role(request)` - Obtiene el rol del usuario desde Auth0 (con cache)
- `is_admin(request)` - Verifica si el usuario es administrador

**Características:**
- ✅ Cache en sesión para evitar llamadas repetidas a Auth0
- ✅ Búsqueda de rol en múltiples formatos (id_token y /userinfo)
- ✅ Normalización de roles (admin, administrador, gerencia campus)
- ✅ Manejo robusto de errores

### 2. `provesi/decorators.py`
**Propósito:** Decoradores reutilizables para control de acceso

**Decorador principal:**
```python
@admin_required
def mi_vista(request):
    # Solo admins pueden acceder
```

**Características:**
- ✅ Combina `@login_required` + validación de rol
- ✅ Redirige con mensaje de error si no es admin
- ✅ Elimina código duplicado en vistas

### 3. `provesi/context_processors.py`
**Propósito:** Inyectar información de rol en todos los templates

**Variables globales en templates:**
- `{{ role }}` - Rol del usuario actual
- `{{ is_admin }}` - Boolean para mostrar/ocultar elementos

**Características:**
- ✅ Disponible en todos los templates automáticamente
- ✅ No necesitas pasar manualmente en cada vista

---

## 🔄 Archivos Modificados

### 1. `provesi/settings.py`
**Cambios:**
```python
# Nuevas configuraciones Auth0
LOGIN_URL = "/login/auth0"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SOCIAL_AUTH_AUTH0_DOMAIN = 'dev-q7qkiq2lfwk64fcv.us.auth0.com'
SOCIAL_AUTH_AUTH0_KEY = 'TK5uVwhkbcLV2jrUkiogvfTqC4BbSqMM'
SOCIAL_AUTH_AUTH0_SECRET = '7xxrCgTjQ-3THYaapKyIEZ9oCFYiYupEoPq0iO6JDOIlHw4DE3xGUWtccwNwXtHi'
SOCIAL_AUTH_AUTH0_SCOPE = ['openid', 'profile', 'email', 'role']

# Backend de autenticación
AUTHENTICATION_BACKENDS = (
    'provesi.auth0backend.Auth0',
    'django.contrib.auth.backends.ModelBackend',
)

# Context processor para roles
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect',
    'provesi.context_processors.auth_info',
]

# App social_django
INSTALLED_APPS += ['social_django']
```

### 2. `provesi/urls.py`
**Cambios:**
```python
urlpatterns = [
    # ... urls existentes
    
    # Auth0 y Django auth
    path('', include('django.contrib.auth.urls')),
    path('', include('social_django.urls')),
    path('logout/', views.logout, name='auth0_logout'),
]
```

### 3. `provesi/views.py`
**Cambios:**
```python
from django.contrib.auth.decorators import login_required

@login_required  # ← Requiere autenticación
def index(request):
    return render(request, 'index.html')

def logout(request):
    """Logout integrado con Auth0"""
    django_logout(request)
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = request.build_absolute_uri('/')
    params = urlencode({'client_id': client_id, 'returnTo': return_to})
    return redirect(f"https://{domain}/v2/logout?{params}")
```

### 4. `manejador_inventario/views.py`
**Antes:**
```python
def bodegas_list(request):
    bodegas = get_bodegas()
    return render(request, 'bodegas_list.html', {'bodegas_list': bodegas})
```

**Después:**
```python
from django.contrib.auth.decorators import login_required
from provesi.decorators import admin_required

# Vistas de lectura (solo login requerido)
@login_required
def bodegas_list(request):
    bodegas = get_bodegas()
    return render(request, 'bodegas_list.html', {'bodegas_list': bodegas})

# Vistas de creación (admin requerido)
@admin_required
def bodega_create(request):
    # Solo admins pueden crear
    if request.method == 'POST':
        form = BodegaForm(request.POST)
        if form.is_valid():
            bodega = create_bodega(form)
            messages.success(request, f"Bodega {bodega.codigo} creada exitosamente.")
            return HttpResponseRedirect(reverse('bodegasList'))
    else:
        form = BodegaForm()
    
    return render(request, 'create_form.html', {...})
```

**Vistas modificadas:**
- ✅ `bodegas_list` - @login_required
- ✅ `bodega_detail` - @login_required
- ✅ `estanteria_detail` - @login_required
- ✅ `productos_list` - @login_required
- ✅ `producto_detail` - @login_required
- ✅ `bodega_create` - @admin_required
- ✅ `estanteria_create` - @admin_required
- ✅ `ubicacion_create` - @admin_required
- ✅ `producto_create` - @admin_required

### 5. `manejador_pedidos/views.py`
**Cambios similares:**
- ✅ `pedidos_list` - @login_required
- ✅ `pedido_detail` - @login_required
- ✅ `pedido_create` - @admin_required
- ✅ `item_create` - @admin_required

### 6. `provesi/templates/base.html`
**Cambios en navbar:**
```django
<nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto">
            <!-- Links de navegación -->
            <li class="nav-item">
                <a class="nav-link" href="{% url 'bodegasList' %}">Bodegas</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="{% url 'pedidosList' %}">Pedidos</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="{% url 'productosList' %}">Productos</a>
            </li>
            
            <!-- Login/Logout -->
            {% if user.is_authenticated %}
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle">
                        Hola, {{ user.first_name }}
                        <br>
                        <small>Rol: {{ role }}</small>
                    </a>
                    <div class="dropdown-menu">
                        <a class="dropdown-item" href="{% url 'auth0_logout' %}">
                            Cerrar Sesión
                        </a>
                    </div>
                </li>
            {% else %}
                <li class="nav-item">
                    <a class="nav-link" href="/login/auth0">Iniciar Sesión</a>
                </li>
            {% endif %}
        </ul>
    </div>
</nav>
```

### 7. Templates de Inventario
**Archivos modificados:**
- `manejador_inventario/templates/bodegas_list.html`
- `manejador_inventario/templates/bodega_detail.html`
- `manejador_inventario/templates/estanteria_detail.html`
- `manejador_inventario/templates/productos_list.html`
- `manejador_inventario/templates/producto_detail.html`

**Cambio aplicado (ejemplo):**
```django
{# Antes: botón siempre visible #}
<button onclick="window.location.href='{% url 'bodegaCreate' %}'">
    Nueva Bodega
</button>

{# Después: botón solo para admins #}
{% if is_admin %}
    <button onclick="window.location.href='{% url 'bodegaCreate' %}'">
        Nueva Bodega
    </button>
{% endif %}
```

### 8. Templates de Pedidos
**Archivos modificados:**
- `manejador_pedidos/templates/pedidos_list.html`
- `manejador_pedidos/templates/pedido_detail.html`

**Cambios similares:** botones condicionados con `{% if is_admin %}`

### 9. `requirements.txt`
**Dependencias añadidas:**
```txt
social-auth-app-django==5.0.0
requests==2.31.0
PyJWT==2.8.0
```

---

## 🔑 Funcionalidades Implementadas

### 1. Sistema de Autenticación
- ✅ Login con Auth0 (OAuth2)
- ✅ Logout integrado (cierra sesión en Django y Auth0)
- ✅ Redirección automática a login si no estás autenticado
- ✅ Persistencia de sesión

### 2. Sistema de Roles
- ✅ Extracción automática de rol desde Auth0
- ✅ Cache de rol en sesión (evita llamadas repetidas)
- ✅ Normalización de roles (admin, administrador, gerencia campus)
- ✅ Rol por defecto: "operario" (solo lectura)

### 3. Control de Acceso en Vistas
- ✅ Vistas de lectura: requieren login (`@login_required`)
- ✅ Vistas de creación: requieren admin (`@admin_required`)
- ✅ Mensajes de error claros si no tienes permisos
- ✅ Redirección automática al home si no es admin

### 4. Control de Acceso en UI
- ✅ Botones de "Crear/Nuevo/Agregar" solo visibles para admins
- ✅ Botones de "Modificar/Editar" solo visibles para admins
- ✅ Indicador de rol en navbar (muestra tu rol actual)
- ✅ Botón de login/logout según estado de autenticación

### 5. Seguridad
- ✅ Todas las vistas protegidas (requieren autenticación)
- ✅ Validación de permisos en servidor (no solo UI)
- ✅ Tokens seguros manejados por Django Social Auth
- ✅ Logout completo (local + Auth0)

---

## 📊 Matriz de Permisos

| Vista | Operario | Admin |
|-------|----------|-------|
| **Ver Listas** (bodegas, productos, pedidos) | ✅ Sí | ✅ Sí |
| **Ver Detalles** (bodega, producto, pedido, estantería) | ✅ Sí | ✅ Sí |
| **Crear Bodega** | ❌ No | ✅ Sí |
| **Crear Estantería** | ❌ No | ✅ Sí |
| **Crear Ubicación** | ❌ No | ✅ Sí |
| **Crear Producto** | ❌ No | ✅ Sí |
| **Crear Pedido** | ❌ No | ✅ Sí |
| **Agregar Ítem** | ❌ No | ✅ Sí |

---

## 🔄 Flujo Simplificado

### Login
```
1. Usuario → Click "Iniciar Sesión"
2. Redirige a Auth0
3. Usuario ingresa credenciales
4. Auth0 valida y genera tokens
5. Callback a Django (/complete/auth0)
6. Django guarda usuario y extrae rol
7. Redirige al home
```

### Navegación (Usuario Autenticado)
```
1. Usuario accede a cualquier vista
2. get_user_role() obtiene rol (desde cache o Auth0)
3. is_admin() verifica si es administrador
4. Vista renderiza con permisos correspondientes
5. Template muestra/oculta botones según is_admin
```

### Intento de Crear (Operario)
```
1. Operario intenta acceder a /bodega/create/
2. @admin_required verifica permisos
3. is_admin(request) → False
4. Redirige al home con mensaje de error
```

### Crear (Admin)
```
1. Admin accede a /bodega/create/
2. @admin_required verifica permisos
3. is_admin(request) → True
4. Permite acceso a formulario
5. Admin crea bodega exitosamente
```

---

## 🎨 Mejoras de UX

### Antes
- ❌ Sin login/logout
- ❌ Todos podían crear/editar
- ❌ Sin control de acceso
- ❌ No se sabía qué rol tenías

### Después
- ✅ Login/logout visible en navbar
- ✅ Solo admins pueden crear/editar
- ✅ Control de acceso en servidor y UI
- ✅ Rol visible en navbar ("Rol: administrador")
- ✅ Mensajes claros si no tienes permisos
- ✅ Botones solo visibles si puedes usarlos

---

## 🧪 Casos de Prueba

### Test 1: Login como Administrador
```
1. Navegar a http://localhost:8080/
2. Click "Iniciar Sesión"
3. Ingresar credenciales de admin
4. Verificar navbar muestra "Rol: administrador"
5. Verificar botones de "Crear" son visibles
6. Crear una bodega → Debe funcionar ✅
```

### Test 2: Login como Operario
```
1. Navegar a http://localhost:8080/
2. Click "Iniciar Sesión"
3. Ingresar credenciales de operario
4. Verificar navbar muestra "Rol: operario"
5. Verificar botones de "Crear" NO son visibles
6. Intentar acceder a /manejador_inventario/bodega/create/
7. Debe redirigir con mensaje de error ✅
```

### Test 3: Usuario Sin Autenticar
```
1. Navegar a http://localhost:8080/
2. Debe redirigir a /login/auth0 ✅
```

### Test 4: Logout
```
1. Estar autenticado
2. Click "Cerrar Sesión"
3. Debe cerrar sesión y redirigir al home
4. Navbar debe mostrar "Iniciar Sesión" ✅
```

---

## 📦 Dependencias Añadidas

```txt
Django==4.2.13                  (ya existía)
psycopg2-binary==2.9.10        (ya existía)
django-bootstrap-v5==1.0.11    (ya existía)
django-widget-tweaks==1.5.0    (ya existía)

social-auth-app-django==5.0.0  ← NUEVA
requests==2.31.0               ← NUEVA
PyJWT==2.8.0                   ← NUEVA
```

---

## ⚙️ Configuración Requerida en Auth0

### 1. Application Settings
```
Type: Regular Web Application
Allowed Callback URLs: http://localhost:8080/complete/auth0
Allowed Logout URLs: http://localhost:8080/
Allowed Web Origins: http://localhost:8080
```

### 2. Action Post-Login
```javascript
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://dev-q7qkiq2lfwk64fcv.us.auth0.com';
  
  // Asignar rol (ejemplo basado en email)
  let role = 'operario';
  if (event.user.email.includes('admin')) {
    role = 'administrador';
  }
  
  // Agregar claim al id_token
  api.idToken.setCustomClaim(`${namespace}/role`, role);
};
```

---

## 🚀 Comandos para Ejecutar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Aplicar migraciones
python manage.py migrate

# 3. Iniciar servidor
python manage.py runserver 0.0.0.0:8080

# 4. Abrir en navegador
# http://localhost:8080/
```

---

## 📝 Resumen Ejecutivo

### ¿Qué se hizo?
Se implementó un sistema completo de autenticación y autorización basado en roles usando Auth0.

### ¿Por qué?
Para controlar el acceso a funcionalidades de creación/edición según el rol del usuario.

### ¿Cómo funciona?
- Auth0 maneja la autenticación (login/logout)
- Django extrae el rol desde Auth0 (id_token o userinfo)
- Decoradores protegen las vistas según rol
- Templates muestran/ocultan elementos según permisos

### ¿Qué se logró?
- ✅ Autenticación segura con Auth0
- ✅ Control de acceso basado en roles
- ✅ Administradores: acceso total
- ✅ Operarios: solo lectura
- ✅ UI adaptativa según permisos
- ✅ Código limpio y mantenible

---

**Desarrollado por:** Equipo SCRUM - ISIS-2503  
**Universidad:** Universidad de los Andes  
**Fecha:** Noviembre 2025

