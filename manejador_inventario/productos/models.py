from django.db import models

# Create your models here.
class Producto(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    nombre = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    
    def __str__(self):
        return f"Producto {self.codigo} - {self.nombre}"