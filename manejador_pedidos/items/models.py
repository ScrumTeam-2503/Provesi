from django.db import models
from pedidos.models import Pedido

# Create your models here.
class Item(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    
    producto = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"Item"