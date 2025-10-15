from django.urls import path
from . import views

urlpatterns = [
    # Ruta para listar todas las bodegas
    path("bodegas/", views.bodegas_list, name="bodegasList"),

    # Ruta para crear una nueva bodega
    path("bodegas/create/", views.bodega_create, name="bodegaCreate"),
]