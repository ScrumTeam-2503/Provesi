from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, EtapaViewSet

router = DefaultRouter()
# items es el prefijo de la url, ItemViewSet es la instruccion  generada en el view
router.register(r"items", ItemViewSet, basename="item")
# (post, gest, put, etc)
# etapas es el prefijo para operaciones CRUD independientes en etapas
router.register(r"etapas", EtapaViewSet, basename="etapa")

urlpatterns = [
    # hace que se usen todas las urls del crud basico que genera el roputer
    path("", include(router.urls)),
]


"""Urls creadas por router:

ITEMS:
GET /items/ → lista todos los items con sus etapas (list)
POST /items/ → crea un nuevo item y opcionalmente sus etapas (create)
GET /items/{id}/ → obtiene un item específico con etapas (retrieve)
PUT /items/{id}/ → actualiza un item completo y sus etapas (update)
PATCH /items/{id}/ → actualiza parcialmente un item (partial_update)
DELETE /items/{id}/ → borra un item y sus etapas (destroy)

ETAPAS:
GET /etapas/ → lista todas las etapas (list)
POST /etapas/ → crea una nueva etapa (create)
GET /etapas/{id}/ → obtiene una etapa específica (retrieve)
PUT /etapas/{id}/ → actualiza una etapa completa (update)
PATCH /etapas/{id}/ → actualiza parcialmente una etapa (partial_update)
DELETE /etapas/{id}/ → borra una etapa (destroy)

Ejemplo de POST para crear Item con Etapas:
{
    "estado": "pendiente",
    "metodo_de_pago": "tarjeta",
    "etapas": [
        {"nombre": "preparacion", "valor": "iniciado"},
        {"nombre": "envio", "valor": "pendiente"}
    ]
}

"""
