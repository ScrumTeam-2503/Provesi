from django.urls import path
from . import views

urlpatterns = [
    # Ruta para listar todos los pedidos
    path("pedidos/", views.pedidos_list, name="pedidosList"),

    # Ruta para ver los detalles de un pedido específico
    #path("pedidos/<int:id>/", views.pedido_detail, name="pedidoDetail")

    # Ruta para crear un nuevo pedido
    path("pedidos/create/", views.pedido_create, name="pedidoCreate"),
]