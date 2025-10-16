from django.urls import path
from . import views

urlpatterns = [
    # Ruta para listar todas las bodegas
    path("bodegas/", views.bodegas_list, name="bodegasList"),

    # Ruta para listar todos los productos
    path("productos/", views.productos_list, name="productosList"),

    # Ruta para crear una nueva bodega
    path("bodegas/create/", views.bodega_create, name="bodegaCreate"),

    # Ruta para crear un nuevo producto
    path("productos/create/", views.producto_create, name="productoCreate"),
    
    # Ruta para ver los detalles de una bodega específica
    path("bodegas/<str:codigo_bodega>/", views.bodega_detail, name="bodegaDetail"),

    # Ruta para ver los detalles de un producto específico
    path("productos/<str:codigo_producto>/", views.producto_detail, name="productoDetail"),

    # Ruta para agregar una estantería a una bodega específica
    path("bodegas/<str:codigo_bodega>/addEstanteria/", views.estanteria_create, name="addEstanteria"),

    # Ruta para ver los detalles de una estantería específica dentro de una bodega
    path("bodegas/<str:codigo_bodega>/<str:zona_estanteria>/<int:codigo_estanteria>/", views.estanteria_detail, name="estanteriaDetail"),

    # Ruta para agregar una ubicación a una estantería específica dentro de una bodega
    path("bodegas/<str:codigo_bodega>/<str:zona_estanteria>/<int:codigo_estanteria>/addUbicacion/", views.ubicacion_create, name="addUbicacion"),
]