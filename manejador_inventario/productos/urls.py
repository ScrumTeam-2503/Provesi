from django.urls import path
from . import views

urlpatterns = [
    path("", views.productos_list, name="productosList"),
    path("<int:codigo>/", views.producto_detail, name="productoDetail")
]