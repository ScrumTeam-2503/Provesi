from django.contrib import admin
from .models import Bodega, Estanteria, Ubicacion, Producto

admin.site.register(Bodega)
admin.site.register(Estanteria)
admin.site.register(Ubicacion)
admin.site.register(Producto)
