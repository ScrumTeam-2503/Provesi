from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item") #items es el prefijo de la url, ItemViewSet es la instruccion  generada en el view
#(post, gest, put, etc)

urlpatterns = [
    path("", include(router.urls)), #hace que se usen todas las urls del crud basico que genera el roputer
]


"""Urls creadas por router:

GET /items/ → lista todos los items (list)

POST /items/ → crea un nuevo item (create)

GET /items/{id}/ → obtiene un item específico (retrieve)

PUT /items/{id}/ → actualiza un item completo (update)

PATCH /items/{id}/ → actualiza parcialmente (partial_update)

DELETE /items/{id}/ → borra un item (destroy)

"""