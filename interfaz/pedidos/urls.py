from django.urls import path
from . import views

urlpatterns = [
    path("", views.pedidos_list, name="pedidosList"),
    path("<int:id>/", views.pedido_detail, name="pedidoDetail")
]